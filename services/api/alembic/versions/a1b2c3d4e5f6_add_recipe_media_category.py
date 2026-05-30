"""add category/cook_minutes/difficulty/image_url to recipe

Revision ID: a1b2c3d4e5f6
Revises: 5456c571037d
Create Date: 2026-05-30 15:30:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: str | None = "5456c571037d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("recipe", schema=None) as batch_op:
        batch_op.add_column(sa.Column("category", sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column("cook_minutes", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("difficulty", sa.String(length=16), nullable=True))
        batch_op.add_column(sa.Column("image_url", sa.String(length=512), nullable=True))
        batch_op.create_index("ix_recipe_category", ["category"], unique=False)


def downgrade() -> None:
    with op.batch_alter_table("recipe", schema=None) as batch_op:
        batch_op.drop_index("ix_recipe_category")
        batch_op.drop_column("image_url")
        batch_op.drop_column("difficulty")
        batch_op.drop_column("cook_minutes")
        batch_op.drop_column("category")
