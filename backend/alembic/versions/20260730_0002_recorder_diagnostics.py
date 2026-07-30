"""Add Hikvision recorder diagnostics.

Revision ID: 20260730_0002
Revises: 20260730_0001
Create Date: 2026-07-30 00:00:01
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260730_0002"
down_revision: str | None = "20260730_0001"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("recorders", sa.Column("hdd_status", sa.String(length=50), nullable=True))
    op.add_column("recorders", sa.Column("hdd_total_bytes", sa.BigInteger(), nullable=True))
    op.add_column("recorders", sa.Column("hdd_free_bytes", sa.BigInteger(), nullable=True))
    op.add_column("recorders", sa.Column("temperature_celsius", sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column("recorders", "temperature_celsius")
    op.drop_column("recorders", "hdd_free_bytes")
    op.drop_column("recorders", "hdd_total_bytes")
    op.drop_column("recorders", "hdd_status")
