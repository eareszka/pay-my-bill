"""admin actions

Revision ID: 0017
Revises: 0016
Create Date: 2026-11-11 18:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0017"
down_revision = "0016"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Who did what in the admin queue, and when (#173).
    op.create_table(
        "admin_actions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("admin_id", sa.Integer(), nullable=True),
        sa.Column("action", sa.String(length=30), nullable=False),
        sa.Column("target", sa.String(length=200), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["admin_id"], ["users.id"], name=op.f("fk_admin_actions_admin_id_users")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_admin_actions")),
    )
    with op.batch_alter_table("admin_actions", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_admin_actions_created_at"), ["created_at"], unique=False
        )


def downgrade() -> None:
    with op.batch_alter_table("admin_actions", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_admin_actions_created_at"))
    op.drop_table("admin_actions")
