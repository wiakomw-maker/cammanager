from pydantic import BaseModel, ConfigDict, Field


class LocationCreate(BaseModel):
    company_id: int
    name: str = Field(max_length=255)
    address: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, max_length=120)


class LocationRead(LocationCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)
