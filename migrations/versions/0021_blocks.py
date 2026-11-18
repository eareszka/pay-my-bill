"""blocks

Revision ID: 0021
Revises: 0020
Create Date: 2026-11-18 16:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0021"
down_revision = "0020"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Blocking another user (#257, App Store Guideline 1.2).
    op.create_table(
        "blocks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("blocker_id", sa.Integer(), nullable=False),
        sa.Column("blocked_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["blocked_id"], ["users.id"], name=op.f("fk_blocks_blocked_id_users")
        ),
        sa.ForeignKeyConstraint(
            ["blocker_id"], ["users.id"], name=op.f("fk_blocks_blocker_id_users")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_blocks")),
        sa.UniqueConstraint("blocker_id", "blocked_id", name="one_block_each"),
    )
    with op.batch_alter_table("blocks", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_blocks_blocked_id"), ["blocked_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_blocks_blocker_id"), ["blocker_id"], unique=False)


def downgrade() -> None:
    with op.batch_alter_table("blocks", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_blocks_blocker_id"))
        batch_op.drop_index(batch_op.f("ix_blocks_blocked_id"))
    op.drop_table("blocks")
