"""intelligence_reports

Revision ID: 003_intelligence_reports
Revises: 002_ingest_logs
Create Date: 2026-05-19

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "003_intelligence_reports"
down_revision: str | None = "002_ingest_logs"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "intelligence_reports",
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
        sa.Column("article_id", sa.Integer(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("tags", sa.JSON(), nullable=False),
        sa.Column("entities", sa.JSON(), nullable=False),
        sa.Column("relevance_score", sa.Float(), nullable=False),
        sa.Column("sentiment", sa.String(length=32), nullable=True),
        sa.Column("language", sa.String(length=32), nullable=True),
        sa.Column("model", sa.String(length=128), nullable=True),
        sa.Column("prompt_template", sa.String(length=128), nullable=True),
        sa.Column("raw_json", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(
            ["article_id"],
            ["articles.id"],
            name=op.f("fk_intelligence_reports_article_id_articles"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_intelligence_reports")),
        sa.UniqueConstraint(
            "article_id", name=op.f("uq_intelligence_reports_article_id")
        ),
    )
    op.create_index(
        op.f("ix_intelligence_reports_article_id"),
        "intelligence_reports",
        ["article_id"],
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_intelligence_reports_article_id"), table_name="intelligence_reports"
    )
    op.drop_table("intelligence_reports")
