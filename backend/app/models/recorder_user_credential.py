from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class RecorderUserCredential(Base):
    __tablename__ = "recorder_user_credentials"
    __table_args__ = (UniqueConstraint("recorder_id", "username", name="uq_recorder_user_credential"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    recorder_id: Mapped[int] = mapped_column(ForeignKey("recorders.id"), nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(32), nullable=False)
    user_level: Mapped[str] = mapped_column(String(32), nullable=False)
    password_encrypted: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
