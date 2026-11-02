"""reactions

Revision ID: 0009
Revises: 0008
Create Date: 2026-11-02 16:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0009"
down_revision = "0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "reactions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("post_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "kind",
            sa.Enum(
                "kudos",
                "up",
                "hmm",
                name="reaction_kind",
                native_enum=False,
                create_constraint=True,
                length=20,
            ),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["post_id"], ["posts.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("post_id", "user_id", "kind", name="one_reaction_each"),
    )
    with op.batch_alter_table("reactions", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_reactions_user_id"), ["user_id"], unique=False)


def downgrade() -> None:
    with op.batch_alter_table("reactions", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_reactions_user_id"))
    op.drop_table("reactions")
