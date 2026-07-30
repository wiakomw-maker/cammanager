from typing import Literal

from pydantic import BaseModel, Field


class RecorderUserRead(BaseModel):
    id: str | None
    username: str
    level: str | None
    has_stored_password: bool = False


class RevealedPassword(BaseModel):
    password: str


class BulkUserCreate(BaseModel):
    username: str = Field(min_length=1, max_length=32, pattern=r"^[A-Za-z0-9_.-]+$")
    password: str = Field(min_length=8, max_length=64)
    user_level: Literal["operator", "user", "viewer"] = "operator"


class BulkUserResult(BaseModel):
    recorder_id: int
    recorder_name: str
    success: bool
    detail: str


class BulkUserCreateResponse(BaseModel):
    results: list[BulkUserResult]
