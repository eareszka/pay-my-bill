"""donations

Revision ID: 0003
Revises: 0002
Create Date: 2026-10-30 14:25:54.375935

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def _enum(name: str, *values: str) -> sa.Enum:
    return sa.Enum(*values, name=name, native_enum=False, create_constraint=True, length=20)


def upgrade() -> None:
    op.create_table(
        "donations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("post_id", sa.Integer(), nullable=False),
        sa.Column("donor_id", sa.Integer(), nullable=False),
        sa.Column("amount_cents", sa.Integer(), nullable=False),
        sa.Column("method", _enum("payment_method", "cashapp", "venmo", "paypal"), nullable=False),
        sa.Column(
            "status",
            _enum("donation_status", "pending", "confirmed", "disputed"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "amount_cents > 0 AND amount_cents <= 100000",
            name=op.f("ck_donations_amount_range"),
        ),
        sa.ForeignKeyConstraint(
            ["donor_id"], ["users.id"], name=op.f("fk_donations_donor_id_users")
        ),
        sa.ForeignKeyConstraint(["post_id"], ["posts.id"], name=op.f("fk_donations_post_id_posts")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_donations")),
    )
    with op.batch_alter_table("donations", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_donations_donor_id"), ["donor_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_donations_post_id"), ["post_id"], unique=False)


def downgrade() -> None:
    with op.batch_alter_table("donations", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_donations_post_id"))
        batch_op.drop_index(batch_op.f("ix_donations_donor_id"))

    op.drop_table("donations")
