from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CompanyCreate(BaseModel):
    name: str = Field(max_length=255)
    nip: str | None = Field(default=None, max_length=20)


class CompanyRead(CompanyCreate):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
