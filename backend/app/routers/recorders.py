import httpx
from fastapi import APIRouter, HTTPException, Response

from app.api.deps import DbSession
from app.models.recorder import Recorder
from app.schemas.hikvision import CameraSyncRead
from app.schemas.recorder import RecorderCreate, RecorderRead
from app.schemas.user import BulkUserCreate, BulkUserCreateResponse, RecorderUserRead, RevealedPassword
from app.services.catalog import CatalogService
from app.services.hikvision import HikvisionService, RecorderNotFoundError

router = APIRouter(prefix="/recorders", tags=["Recorders"])
service = CatalogService(Recorder)
hikvision_service = HikvisionService()


@router.get("", response_model=list[RecorderRead])
async def list_recorders(session: DbSession) -> list[Recorder]:
    return await service.list(session)


@router.post("", response_model=RecorderRead, status_code=201)
async def create_recorder(payload: RecorderCreate, session: DbSession) -> Recorder:
    return await service.create(session, payload.model_dump())


@router.post("/bulk-users", response_model=BulkUserCreateResponse)
async def create_user_on_all_recorders(payload: BulkUserCreate, session: DbSession) -> BulkUserCreateResponse:
    return BulkUserCreateResponse(results=await hikvision_service.create_user_on_all(session, payload))


@router.delete("/{recorder_id}", status_code=204)
async def delete_recorder(recorder_id: int, session: DbSession) -> Response:
    try:
        await hikvision_service.delete_recorder(session, recorder_id)
    except RecorderNotFoundError as error:
        raise HTTPException(status_code=404, detail="Recorder not found") from error
    return Response(status_code=204)


@router.get("/{recorder_id}/users", response_model=list[RecorderUserRead])
async def list_recorder_users(recorder_id: int, session: DbSession) -> list[RecorderUserRead]:
    try:
        return await hikvision_service.users(session, recorder_id)
    except RecorderNotFoundError as error:
        raise HTTPException(status_code=404, detail="Recorder not found") from error
    except httpx.HTTPError as error:
        raise HTTPException(status_code=502, detail="Unable to retrieve Hikvision users") from error


@router.post("/{recorder_id}/users/{username}/reveal-password", response_model=RevealedPassword)
async def reveal_recorder_user_password(recorder_id: int, username: str, session: DbSession) -> RevealedPassword:
    try:
        return RevealedPassword(password=await hikvision_service.reveal_user_password(session, recorder_id, username))
    except RecorderNotFoundError as error:
        raise HTTPException(status_code=404, detail="Stored password not found") from error
    except RuntimeError as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


@router.post("/{recorder_id}/refresh", response_model=RecorderRead)
async def refresh_recorder(recorder_id: int, session: DbSession) -> Recorder:
    try:
        return await hikvision_service.refresh(session, recorder_id)
    except RecorderNotFoundError as error:
        raise HTTPException(status_code=404, detail="Recorder not found") from error


@router.post("/{recorder_id}/sync", response_model=CameraSyncRead)
async def sync_recorder_cameras(recorder_id: int, session: DbSession) -> CameraSyncRead:
    try:
        created, updated, total = await hikvision_service.sync_cameras(session, recorder_id)
    except RecorderNotFoundError as error:
        raise HTTPException(status_code=404, detail="Recorder not found") from error
    except httpx.HTTPError as error:
        raise HTTPException(status_code=502, detail="Unable to synchronize Hikvision recorder") from error
    return CameraSyncRead(recorder_id=recorder_id, created=created, updated=updated, total=total)


@router.get("/{recorder_id}/cameras/{camera_id}/snapshot", response_class=Response)
async def get_camera_snapshot(recorder_id: int, camera_id: int, session: DbSession) -> Response:
    try:
        content, media_type = await hikvision_service.snapshot(session, recorder_id, camera_id)
    except RecorderNotFoundError as error:
        raise HTTPException(status_code=404, detail="Camera or recorder not found") from error
    except httpx.HTTPError as error:
        raise HTTPException(status_code=502, detail="Unable to fetch Hikvision snapshot") from error
    return Response(content=content, media_type=media_type)
