from fastapi import APIRouter

from app.api.deps import DbSession
from app.models.location import Location
from app.schemas.location import LocationCreate, LocationRead
from app.services.catalog import CatalogService

router = APIRouter(prefix="/locations", tags=["Locations"])
service = CatalogService(Location)


@router.get("", response_model=list[LocationRead])
async def list_locations(session: DbSession) -> list[Location]:
    return await service.list(session)


@router.post("", response_model=LocationRead, status_code=201)
async def create_location(payload: LocationCreate, session: DbSession) -> Location:
    return await service.create(session, payload.model_dump())
