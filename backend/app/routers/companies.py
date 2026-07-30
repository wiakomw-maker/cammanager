from fastapi import APIRouter

from app.api.deps import DbSession
from app.models.company import Company
from app.schemas.company import CompanyCreate, CompanyRead
from app.services.catalog import CatalogService

router = APIRouter(prefix="/companies", tags=["Companies"])
service = CatalogService(Company)


@router.get("", response_model=list[CompanyRead])
async def list_companies(session: DbSession) -> list[Company]:
    return await service.list(session)


@router.post("", response_model=CompanyRead, status_code=201)
async def create_company(payload: CompanyCreate, session: DbSession) -> Company:
    return await service.create(session, payload.model_dump())
