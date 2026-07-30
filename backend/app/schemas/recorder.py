from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RecorderCreate(BaseModel):
    location_id: int
    name: str = Field(max_length=255)
    model: str | None = Field(default=None, max_length=255)
    serial: str | None = Field(default=None, max_length=255)
    firmware: str | None = Field(default=None, max_length=255)
    ip: str = Field(max_length=45)
    port: int = Field(default=443, ge=1, le=65535)
    username: str = Field(max_length=255)
    password: str = Field(max_length=255)
    https: bool = True


class RecorderRead(BaseModel):
    id: int
    location_id: int
    name: str
    model: str | None
    serial: str | None
    firmware: str | None
    ip: str
    port: int
    username: str
    https: bool
    last_seen: datetime | None
    status: str | None
    model_config = ConfigDict(from_attributes=True)
