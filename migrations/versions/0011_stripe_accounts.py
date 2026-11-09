"""stripe connect accounts

Revision ID: 0011
Revises: 0010
Create Date: 2026-11-09 00:02:38.917672

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0011"
down_revision = "0010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(sa.Column("stripe_account_id", sa.String(length=64), nullable=True))
        batch_op.add_column(
            sa.Column("stripe_ready", sa.Boolean(), server_default="0", nullable=False)
        )
        batch_op.create_unique_constraint(
            batch_op.f("uq_users_stripe_account_id"), ["stripe_account_id"]
        )


def downgrade() -> None:
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f("uq_users_stripe_account_id"), type_="unique")
        batch_op.drop_column("stripe_ready")
        batch_op.drop_column("stripe_account_id")
