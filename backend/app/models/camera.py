from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Camera(Base):
    __tablename__ = "cameras"
    __table_args__ = (UniqueConstraint("recorder_id", "channel", name="uq_camera_recorder_channel"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    recorder_id: Mapped[int] = mapped_column(ForeignKey("recorders.id"), nullable=False, index=True)
    channel: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    model: Mapped[str | None] = mapped_column(String(255))
    serial: Mapped[str | None] = mapped_column(String(255))
    ip: Mapped[str | None] = mapped_column(String(45))
    mac: Mapped[str | None] = mapped_column(String(17))
    firmware: Mapped[str | None] = mapped_column(String(255))
    online: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_snapshot: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str | None] = mapped_column(String(50))
    recorder: Mapped["Recorder"] = relationship(back_populates="cameras")
