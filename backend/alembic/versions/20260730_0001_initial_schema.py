"""Create CAM Manager core tables.

Revision ID: 20260730_0001
Revises:
Create Date: 2026-07-30 00:00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260730_0001"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "companies",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("nip", sa.String(length=20), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("nip"),
    )
    op.create_table(
        "locations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("address", sa.String(length=255), nullable=True),
        sa.Column("city", sa.String(length=120), nullable=True),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_locations_company_id", "locations", ["company_id"])
    op.create_table(
        "recorders",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("location_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("model", sa.String(length=255), nullable=True),
        sa.Column("serial", sa.String(length=255), nullable=True),
        sa.Column("firmware", sa.String(length=255), nullable=True),
        sa.Column("ip", sa.String(length=45), nullable=False),
        sa.Column("port", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=255), nullable=False),
        sa.Column("password", sa.String(length=255), nullable=False),
        sa.Column("https", sa.Boolean(), nullable=False),
        sa.Column("last_seen", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(["location_id"], ["locations.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("serial"),
    )
    op.create_index("ix_recorders_location_id", "recorders", ["location_id"])
    op.create_table(
        "cameras",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("recorder_id", sa.Integer(), nullable=False),
        sa.Column("channel", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("model", sa.String(length=255), nullable=True),
        sa.Column("serial", sa.String(length=255), nullable=True),
        sa.Column("ip", sa.String(length=45), nullable=True),
        sa.Column("mac", sa.String(length=17), nullable=True),
        sa.Column("firmware", sa.String(length=255), nullable=True),
        sa.Column("online", sa.Boolean(), nullable=False),
        sa.Column("last_snapshot", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(["recorder_id"], ["recorders.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("recorder_id", "channel", name="uq_camera_recorder_channel"),
    )
    op.create_index("ix_cameras_recorder_id", "cameras", ["recorder_id"])


def downgrade() -> None:
    op.drop_index("ix_cameras_recorder_id", table_name="cameras")
    op.drop_table("cameras")
    op.drop_index("ix_recorders_location_id", table_name="recorders")
    op.drop_table("recorders")
    op.drop_index("ix_locations_company_id", table_name="locations")
    op.drop_table("locations")
    op.drop_table("companies")
