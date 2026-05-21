"""daily_archives

Revision ID: 006_daily_archives
Revises: 005_briefing_delivery_logs
Create Date: 2026-05-21

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "006_daily_archives"
down_revision: str | None = "005_briefing_delivery_logs"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "daily_archives",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("archive_date", sa.Date(), nullable=False),
        sa.Column("timezone", sa.String(length=64), nullable=False),
        sa.Column("window_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("window_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("briefing_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("metrics_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_daily_archives")),
        sa.UniqueConstraint("archive_date", name=op.f("uq_daily_archives_archive_date")),
    )
    op.create_index(
        "ix_daily_archives_archive_date_desc",
        "daily_archives",
        [sa.text("archive_date DESC")],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_daily_archives_archive_date_desc", table_name="daily_archives")
    op.drop_table("daily_archives")
