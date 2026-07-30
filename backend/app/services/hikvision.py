from datetime import datetime, timezone
from xml.etree import ElementTree

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.hikvision.client import HikvisionClient, HikvisionConnection
from app.models.camera import Camera
from app.models.recorder import Recorder
from app.models.recorder_user_credential import RecorderUserCredential
from app.schemas.user import BulkUserCreate, BulkUserResult, RecorderUserRead
from app.services.credentials import CredentialVault


class RecorderNotFoundError(Exception):
    pass


class HikvisionService:
    def __init__(self) -> None:
        self._vault = CredentialVault()

    def _client(self, recorder: Recorder) -> HikvisionClient:
        settings = get_settings()
        return HikvisionClient(
            HikvisionConnection(recorder.ip, recorder.port, recorder.username, recorder.password, recorder.https),
            verify_tls=settings.hikvision_verify_tls,
            timeout_seconds=settings.hikvision_request_timeout_seconds,
        )

    async def get_recorder(self, session: AsyncSession, recorder_id: int) -> Recorder:
        recorder = await session.get(Recorder, recorder_id)
        if recorder is None:
            raise RecorderNotFoundError
        return recorder

    async def refresh(self, session: AsyncSession, recorder_id: int) -> Recorder:
        recorder = await self.get_recorder(session, recorder_id)
        try:
            async with self._client(recorder) as client:
                info = await client.device_info()
                try:
                    recorder.status = await client.system_status()
                except (httpx.HTTPError, ElementTree.ParseError):
                    recorder.status = "online"
                try:
                    storage = await client.storage_info()
                except (httpx.HTTPError, ElementTree.ParseError):
                    storage = {"status": None, "total": None, "free": None}
                try:
                    recorder.temperature_celsius = await client.temperature()
                except (httpx.HTTPError, ElementTree.ParseError):
                    recorder.temperature_celsius = None
        except (httpx.HTTPError, ElementTree.ParseError):
            recorder.status = "offline"
            await session.commit()
            await session.refresh(recorder)
            return recorder

        recorder.model = info["model"] or recorder.model
        recorder.serial = info["serial"] or recorder.serial
        recorder.firmware = info["firmware"] or recorder.firmware
        recorder.hdd_status = storage["status"] if isinstance(storage["status"], str) else None
        recorder.hdd_total_bytes = storage["total"] if isinstance(storage["total"], int) else None
        recorder.hdd_free_bytes = storage["free"] if isinstance(storage["free"], int) else None
        recorder.last_seen = datetime.now(timezone.utc)
        await session.commit()
        await session.refresh(recorder)
        return recorder

    async def sync_cameras(self, session: AsyncSession, recorder_id: int) -> tuple[int, int, int]:
        recorder = await self.get_recorder(session, recorder_id)
        async with self._client(recorder) as client:
            channels = await client.input_channels()

        existing = {
            camera.channel: camera
            for camera in await session.scalars(select(Camera).where(Camera.recorder_id == recorder_id))
        }
        created = 0
        updated = 0
        for data in channels:
            camera = existing.get(data["channel"])
            if camera is None:
                session.add(Camera(recorder_id=recorder_id, **data))
                created += 1
                continue
            for field, value in data.items():
                setattr(camera, field, value)
            updated += 1
        await session.commit()
        return created, updated, len(channels)

    async def snapshot(self, session: AsyncSession, recorder_id: int, camera_id: int) -> tuple[bytes, str]:
        camera = await session.get(Camera, camera_id)
        if camera is None or camera.recorder_id != recorder_id:
            raise RecorderNotFoundError
        recorder = await self.get_recorder(session, recorder_id)
        async with self._client(recorder) as client:
            content, media_type = await client.snapshot(camera.channel)
        camera.last_snapshot = datetime.now(timezone.utc)
        await session.commit()
        return content, media_type

    async def delete_recorder(self, session: AsyncSession, recorder_id: int) -> None:
        recorder = await self.get_recorder(session, recorder_id)
        cameras = await session.scalars(select(Camera).where(Camera.recorder_id == recorder_id))
        for camera in cameras:
            await session.delete(camera)
        await session.delete(recorder)
        await session.commit()

    async def users(self, session: AsyncSession, recorder_id: int) -> list[RecorderUserRead]:
        recorder = await self.get_recorder(session, recorder_id)
        async with self._client(recorder) as client:
            users = await client.users()
        stored = set(await session.scalars(select(RecorderUserCredential.username).where(RecorderUserCredential.recorder_id == recorder_id)))
        return [RecorderUserRead(**user, has_stored_password=user["username"] in stored) for user in users]

    async def reveal_user_password(self, session: AsyncSession, recorder_id: int, username: str) -> str:
        credential = await session.scalar(select(RecorderUserCredential).where(RecorderUserCredential.recorder_id == recorder_id, RecorderUserCredential.username == username))
        if credential is None:
            raise RecorderNotFoundError
        return self._vault.decrypt(credential.password_encrypted)

    async def create_user_on_all(self, session: AsyncSession, payload: BulkUserCreate) -> list[BulkUserResult]:
        recorders = list(await session.scalars(select(Recorder).order_by(Recorder.id)))

        results: list[BulkUserResult] = []
        for recorder in recorders:
            try:
                async with self._client(recorder) as client:
                    await client.create_user(payload.username, payload.password, payload.user_level)
                session.add(RecorderUserCredential(recorder_id=recorder.id, username=payload.username, user_level=payload.user_level, password_encrypted=self._vault.encrypt(payload.password)))
                results.append(BulkUserResult(recorder_id=recorder.id, recorder_name=recorder.name, success=True, detail="User created"))
            except httpx.HTTPError as error:
                status = error.response.status_code if isinstance(error, httpx.HTTPStatusError) else None
                detail = "User already exists" if status == 409 else "Unable to create user"
                results.append(BulkUserResult(recorder_id=recorder.id, recorder_name=recorder.name, success=False, detail=detail))
        await session.commit()
        return results
