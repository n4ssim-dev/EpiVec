"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-05-22
"""

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # regions — doit être créée avant indicators (FK)
    op.create_table(
        "regions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("code", sa.String(20), nullable=False),
        sa.Column("level", sa.String(20), nullable=True),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["parent_id"], ["regions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_regions_code", "regions", ["code"], unique=True)

    # triples — triplets de connaissance (sujet, prédicat, objet)
    op.create_table(
        "triples",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("subject", sa.String(500), nullable=False),
        sa.Column("predicate", sa.String(200), nullable=False),
        sa.Column("object", sa.String(500), nullable=False),
        sa.Column("source", sa.String(100), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_triples_subject", "triples", ["subject"])
    op.create_index("ix_triples_predicate", "triples", ["predicate"])

    # indicators — séries temporelles épidémiologiques
    op.create_table(
        "indicators",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("disease", sa.String(200), nullable=False),
        sa.Column("region_code", sa.String(20), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("metric", sa.String(100), nullable=True),
        sa.Column("value", sa.Float(), nullable=True),
        sa.Column("source", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["region_code"], ["regions.code"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_indicators_disease", "indicators", ["disease"])
    op.create_index("ix_indicators_region_code", "indicators", ["region_code"])
    op.create_index("ix_indicators_date", "indicators", ["date"])


def downgrade() -> None:
    op.drop_index("ix_indicators_date", "indicators")
    op.drop_index("ix_indicators_region_code", "indicators")
    op.drop_index("ix_indicators_disease", "indicators")
    op.drop_table("indicators")

    op.drop_index("ix_triples_predicate", "triples")
    op.drop_index("ix_triples_subject", "triples")
    op.drop_table("triples")

    op.drop_index("ix_regions_code", "regions")
    op.drop_table("regions")
