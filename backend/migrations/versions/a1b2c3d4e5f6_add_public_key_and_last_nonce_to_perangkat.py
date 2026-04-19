# Migration: add public_key and last_nonce to perangkat table
"""add_public_key_and_last_nonce_to_perangkat

Revision ID: a1b2c3d4e5f6
Revises: 66cbfbd60f7a
Create Date: 2026-04-15 01:30:00
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f6"
down_revision = "66cbfbd60f7a"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('perangkat', sa.Column('public_key', sa.Text(), nullable=True))
    op.add_column('perangkat', sa.Column('last_nonce', sa.BigInteger(), nullable=True))


def downgrade():
    op.drop_column('perangkat', 'last_nonce')
    op.drop_column('perangkat', 'public_key')
