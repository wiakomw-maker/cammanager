from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CameraCreate(BaseModel):
    recorder_id: int
    channel: int = Field(ge=1)
    name: str = Field(max_length=255)
    model: str | None = Field(default=None, max_length=255)
    serial: str | None = Field(default=None, max_length=255)
    ip: str | None = Field(default=None, max_length=45)
    mac: str | None = Field(default=None, max_length=17)
    firmware: str | None = Field(default=None, max_length=255)


class CameraRead(CameraCreate):
    id: int
    online: bool
    last_snapshot: datetime | None
    status: str | None
    model_config = ConfigDict(from_attributes=True)
