from fastapi import APIRouter

from app.api.deps import DbSession
from app.models.camera import Camera
from app.schemas.camera import CameraCreate, CameraRead
from app.services.catalog import CatalogService

router = APIRouter(prefix="/cameras", tags=["Cameras"])
service = CatalogService(Camera)


@router.get("", response_model=list[CameraRead])
async def list_cameras(session: DbSession) -> list[Camera]:
    return await service.list(session)


@router.post("", response_model=CameraRead, status_code=201)
async def create_camera(payload: CameraCreate, session: DbSession) -> Camera:
    return await service.create(session, payload.model_dump())
