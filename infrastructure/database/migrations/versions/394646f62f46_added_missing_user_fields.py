"""added missing user fields

Revision ID: 394646f62f46
Revises: 12aa266eab1f
Create Date: 2025-07-27 11:51:39.571405

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '394646f62f46'
down_revision: Union[str, Sequence[str], None] = '12aa266eab1f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('age', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('gender', sa.String(), nullable=True))
    op.add_column('users', sa.Column('activity_level', sa.String(), nullable=True))
    op.add_column('users', sa.Column('goal', sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'goal')
    op.drop_column('users', 'activity_level')
    op.drop_column('users', 'gender')
    op.drop_column('users', 'age')
