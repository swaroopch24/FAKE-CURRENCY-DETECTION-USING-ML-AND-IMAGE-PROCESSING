"""make_user_id_nullable

Revision ID: 3ed6213f975a
Revises: 9f312da84ab1
Create Date: 2026-08-15 15:00:50.172132

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3ed6213f975a'
down_revision: Union[str, None] = '9f312da84ab1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('currency_verifications', 'user_id',
               existing_type=sa.UUID(),
               nullable=True)


def downgrade() -> None:
    op.alter_column('currency_verifications', 'user_id',
               existing_type=sa.UUID(),
               nullable=False)
