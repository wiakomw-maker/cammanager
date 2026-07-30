from datetime import datetime, timezone
from xml.etree import ElementTree

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.hikvision.client import HikvisionClient, HikvisionConnection
from app.models.camera import Camera
from app.models.recorder import Recorder


class RecorderNotFoundError(Exception):
    pass


class HikvisionService:
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
