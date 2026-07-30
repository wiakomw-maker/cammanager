from fastapi import APIRouter

from app.api.deps import DbSession
from app.models.recorder import Recorder
from app.schemas.recorder import RecorderCreate, RecorderRead
from app.services.catalog import CatalogService

router = APIRouter(prefix="/recorders", tags=["Recorders"])
service = CatalogService(Recorder)


@router.get("", response_model=list[RecorderRead])
async def list_recorders(session: DbSession) -> list[Recorder]:
    return await service.list(session)


@router.post("", response_model=RecorderRead, status_code=201)
async def create_recorder(payload: RecorderCreate, session: DbSession) -> Recorder:
    return await service.create(session, payload.model_dump())
