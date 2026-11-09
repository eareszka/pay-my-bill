"""card gifts

Revision ID: 0012
Revises: 0011
Create Date: 2026-11-09 00:21:32.529994

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0012"
down_revision = "0011"
branch_labels = None
depends_on = None

OLD_METHODS = "method IN ('cashapp', 'venmo', 'paypal')"
NEW_METHODS = "method IN ('cashapp', 'venmo', 'paypal', 'card')"


def upgrade() -> None:
    with op.batch_alter_table("donations", schema=None) as batch_op:
        batch_op.add_column(sa.Column("stripe_session_id", sa.String(length=255), nullable=True))
        batch_op.add_column(
            sa.Column("stripe_payment_intent", sa.String(length=255), nullable=True)
        )
        batch_op.add_column(
            sa.Column("fee_cents", sa.Integer(), server_default="0", nullable=False)
        )
        batch_op.create_index(
            batch_op.f("ix_donations_stripe_payment_intent"),
            ["stripe_payment_intent"],
            unique=False,
        )
        batch_op.create_unique_constraint(
            batch_op.f("uq_donations_stripe_session_id"), ["stripe_session_id"]
        )
        # Card gifts are a new payment method (ADR 0014).
        batch_op.drop_constraint("payment_method", type_="check")
        batch_op.create_check_constraint("payment_method", NEW_METHODS)


def downgrade() -> None:
    op.execute("DELETE FROM donations WHERE method = 'card'")
    with op.batch_alter_table("donations", schema=None) as batch_op:
        batch_op.drop_constraint("payment_method", type_="check")
        batch_op.create_check_constraint("payment_method", OLD_METHODS)
        batch_op.drop_constraint(batch_op.f("uq_donations_stripe_session_id"), type_="unique")
        batch_op.drop_index(batch_op.f("ix_donations_stripe_payment_intent"))
        batch_op.drop_column("fee_cents")
        batch_op.drop_column("stripe_payment_intent")
        batch_op.drop_column("stripe_session_id")
