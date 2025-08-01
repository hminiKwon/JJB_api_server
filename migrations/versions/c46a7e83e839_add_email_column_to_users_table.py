"""Add email column to users table

Revision ID: c46a7e83e839
Revises: f151f747cd07
Create Date: 2025-07-24 11:40:38.619742

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c46a7e83e839'
down_revision: Union[str, Sequence[str], None] = 'f151f747cd07'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('partner_id', sa.Integer(), nullable=False))
    op.create_index(op.f('ix_user_partner_id'), 'user', ['partner_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_partner_id'), table_name='user')
    op.drop_column('user', 'partner_id')
    # ### end Alembic commands ###
