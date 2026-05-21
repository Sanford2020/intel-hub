"""sources last_ingested_at + ingest_logs

Revision ID: 002_ingest_logs
Revises: 001_sources_articles
Create Date: 2026-05-19

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "002_ingest_logs"
down_revision: str | None = "001_sources_articles"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "sources",
        sa.Column("last_ingested_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table(
        "ingest_logs",
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
        sa.Column("source_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("items_found", sa.Integer(), nullable=False),
        sa.Column("items_created", sa.Integer(), nullable=False),
        sa.Column("items_skipped", sa.Integer(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["source_id"],
            ["sources.id"],
            name=op.f("fk_ingest_logs_source_id_sources"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_ingest_logs")),
    )
    op.create_index(op.f("ix_ingest_logs_source_id"), "ingest_logs", ["source_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_ingest_logs_source_id"), table_name="ingest_logs")
    op.drop_table("ingest_logs")
    op.drop_column("sources", "last_ingested_at")
