"""Add audit log table

Revision ID: e7f7ef216f41
Revises: 9e997f33c9fd
Create Date: 2026-04-05 08:15:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e7f7ef216f41"
down_revision = "86f7d3d8a1b2"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "audit_log",
        sa.Column("id_log", sa.Integer(), nullable=False),
        sa.Column("id_user", sa.Integer(), nullable=True),
        sa.Column("aksi", sa.String(length=10), nullable=False),
        sa.Column("tabel", sa.String(length=50), nullable=False),
        sa.Column("record_pk", sa.String(length=50), nullable=False),
        sa.Column("timestamp", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("old_value", sa.Text(), nullable=True),
        sa.Column("new_value", sa.Text(), nullable=True),
        sa.CheckConstraint("aksi IN ('INSERT', 'UPDATE', 'DELETE')", name="ck_audit_log_aksi_valid"),
        sa.ForeignKeyConstraint(["id_user"], ["users.id_user"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id_log"),
    )


def downgrade():
    op.drop_table("audit_log")
