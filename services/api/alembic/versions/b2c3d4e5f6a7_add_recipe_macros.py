"""add total_protein_g/carb_g/fat_g/fiber_g to recipe

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-06-09 10:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "b2c3d4e5f6a7"
down_revision: str | None = "a1b2c3d4e5f6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("recipe", schema=None) as batch_op:
        batch_op.add_column(sa.Column("total_protein_g", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("total_carb_g", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("total_fat_g", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("total_fiber_g", sa.Float(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("recipe", schema=None) as batch_op:
        batch_op.drop_column("total_fiber_g")
        batch_op.drop_column("total_fat_g")
        batch_op.drop_column("total_carb_g")
        batch_op.drop_column("total_protein_g")
