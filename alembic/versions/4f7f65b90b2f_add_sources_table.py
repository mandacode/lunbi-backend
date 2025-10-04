"""add sources table

Revision ID: 4f7f65b90b2f
Revises: 728487261ea4
Create Date: 2025-10-04 13:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "4f7f65b90b2f"
down_revision: Union[str, Sequence[str], None] = "728487261ea4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "sources",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("md_filename", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("url"),
        sa.UniqueConstraint("md_filename"),
    )
    op.create_index(op.f("ix_sources_id"), "sources", ["id"], unique=False)
    op.create_index(op.f("ix_sources_md_filename"), "sources", ["md_filename"], unique=True)

    op.add_column("prompts", sa.Column("source_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "prompts_source_id_fkey",
        "prompts",
        "sources",
        ["source_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("prompts_source_id_fkey", "prompts", type_="foreignkey")
    op.drop_column("prompts", "source_id")
    op.drop_index(op.f("ix_sources_md_filename"), table_name="sources")
    op.drop_index(op.f("ix_sources_id"), table_name="sources")
    op.drop_table("sources")
