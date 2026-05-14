"""add_description_to_points_rules

Revision ID: 3712add79c8d
Revises: 3711fbb22d6c
Create Date: 2026-05-14 10:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '3712add79c8d'
down_revision: Union[str, None] = '3711fbb22d6c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('points_rules', sa.Column('description', sa.Text(), nullable=True, comment='规则描述'))


def downgrade() -> None:
    op.drop_column('points_rules', 'description')
