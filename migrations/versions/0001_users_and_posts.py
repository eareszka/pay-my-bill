"""users and posts

Revision ID: 0001
Revises:
Create Date: 2026-10-27 23:04:27.049958

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=30), nullable=False),
        sa.Column("email", sa.String(length=254), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("email_verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("city", sa.String(length=80), nullable=True),
        sa.Column("state", sa.String(length=2), nullable=True),
        sa.Column("cashapp_handle", sa.String(length=40), nullable=True),
        sa.Column("venmo_handle", sa.String(length=40), nullable=True),
        sa.Column("paypal_handle", sa.String(length=40), nullable=True),
        sa.Column("rules_accepted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_admin", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("email", name=op.f("uq_users_email")),
        sa.UniqueConstraint("username", name=op.f("uq_users_username")),
    )
    op.create_table(
        "posts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "kind",
            sa.Enum(
                "want",
                "need",
                name="post_kind",
                native_enum=False,
                create_constraint=True,
                length=20,
            ),
            nullable=False,
        ),
        sa.Column("title", sa.String(length=80), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("goal_cents", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "pending_review",
                "open",
                "funded",
                "closed",
                "removed",
                name="post_status",
                native_enum=False,
                create_constraint=True,
                length=20,
            ),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "goal_cents > 0 AND goal_cents <= 100000", name=op.f("ck_posts_goal_range")
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_posts_user_id_users")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_posts")),
    )
    with op.batch_alter_table("posts", schema=None) as batch_op:
        batch_op.create_index("ix_posts_status_created_at", ["status", "created_at"], unique=False)
        batch_op.create_index(batch_op.f("ix_posts_user_id"), ["user_id"], unique=False)


def downgrade() -> None:
    with op.batch_alter_table("posts", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_posts_user_id"))
        batch_op.drop_index("ix_posts_status_created_at")

    op.drop_table("posts")
    op.drop_table("users")
