"""Store encrypted created recorder user credentials.

Revision ID: 20260731_0003
Revises: 20260730_0002
"""
import sqlalchemy as sa
from alembic import op

revision = "20260731_0003"
down_revision = "20260730_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("recorder_user_credentials", sa.Column("id", sa.Integer(), nullable=False), sa.Column("recorder_id", sa.Integer(), nullable=False), sa.Column("username", sa.String(length=32), nullable=False), sa.Column("user_level", sa.String(length=32), nullable=False), sa.Column("password_encrypted", sa.String(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.ForeignKeyConstraint(["recorder_id"], ["recorders.id"]), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("recorder_id", "username", name="uq_recorder_user_credential"))
    op.create_index("ix_recorder_user_credentials_recorder_id", "recorder_user_credentials", ["recorder_id"])


def downgrade() -> None:
    op.drop_index("ix_recorder_user_credentials_recorder_id", table_name="recorder_user_credentials")
    op.drop_table("recorder_user_credentials")
