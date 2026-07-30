from datetime import datetime

from pydantic import BaseModel


class RecorderRefreshRead(BaseModel):
    recorder_id: int
    status: str
    last_seen: datetime | None
    model: str | None
    serial: str | None
    firmware: str | None
    hdd_status: str | None
    hdd_total_bytes: int | None
    hdd_free_bytes: int | None
    temperature_celsius: float | None


class CameraSyncRead(BaseModel):
    recorder_id: int
    created: int
    updated: int
    total: int
