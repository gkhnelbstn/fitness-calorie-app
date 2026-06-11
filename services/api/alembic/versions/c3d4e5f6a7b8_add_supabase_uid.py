"""add supabase_uid to user_profile

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-06-10 12:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "c3d4e5f6a7b8"
down_revision: str | None = "b2c3d4e5f6a7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("user_profile", schema=None) as batch_op:
        batch_op.add_column(sa.Column("supabase_uid", sa.String(length=36), nullable=True))
        batch_op.create_index("ix_user_profile_supabase_uid", ["supabase_uid"], unique=True)


def downgrade() -> None:
    with op.batch_alter_table("user_profile", schema=None) as batch_op:
        batch_op.drop_index("ix_user_profile_supabase_uid")
        batch_op.drop_column("supabase_uid")
