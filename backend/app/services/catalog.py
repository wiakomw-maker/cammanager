from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class CatalogService(Generic[ModelT]):
    def __init__(self, model: type[ModelT]) -> None:
        self.model = model

    async def list(self, session: AsyncSession) -> list[ModelT]:
        result = await session.scalars(select(self.model).order_by(self.model.id))
        return list(result)

    async def create(self, session: AsyncSession, data: dict[str, object]) -> ModelT:
        entity = self.model(**data)
        session.add(entity)
        await session.commit()
        await session.refresh(entity)
        return entity
