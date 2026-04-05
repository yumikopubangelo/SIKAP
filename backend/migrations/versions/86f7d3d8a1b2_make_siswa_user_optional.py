"""Make siswa user optional

Revision ID: 86f7d3d8a1b2
Revises: 9e997f33c9fd
Create Date: 2026-04-04 23:15:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "86f7d3d8a1b2"
down_revision = "9e997f33c9fd"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("siswa") as batch_op:
        batch_op.alter_column(
            "id_user",
            existing_type=sa.Integer(),
            nullable=True,
        )


def downgrade():
    with op.batch_alter_table("siswa") as batch_op:
        batch_op.alter_column(
            "id_user",
            existing_type=sa.Integer(),
            nullable=False,
        )
