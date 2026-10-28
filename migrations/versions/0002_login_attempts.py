"""login attempts

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-28 03:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "login_attempts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("identifier", sa.String(length=254), nullable=False),
        sa.Column("ip", sa.String(length=45), nullable=True),
        sa.Column("succeeded", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_login_attempts")),
    )
    with op.batch_alter_table("login_attempts", schema=None) as batch_op:
        batch_op.create_index(
            "ix_login_attempts_identifier_created_at", ["identifier", "created_at"], unique=False
        )


def downgrade() -> None:
    with op.batch_alter_table("login_attempts", schema=None) as batch_op:
        batch_op.drop_index("ix_login_attempts_identifier_created_at")

    op.drop_table("login_attempts")
