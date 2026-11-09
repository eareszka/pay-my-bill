"""reports and bans

Revision ID: 0010
Revises: 0009
Create Date: 2026-11-08 21:10:32.404180

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0010"
down_revision = "0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "reports",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("reporter_id", sa.Integer(), nullable=False),
        sa.Column("post_id", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column(
            "reason",
            sa.Enum(
                "scam",
                "business",
                "harassment",
                "private_info",
                "spam",
                "other",
                name="report_reason",
                native_enum=False,
                create_constraint=True,
                length=20,
            ),
            nullable=False,
        ),
        sa.Column("details", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolution", sa.String(length=20), nullable=True),
        sa.CheckConstraint(
            "(post_id IS NULL) <> (user_id IS NULL)", name=op.f("ck_reports_one_target")
        ),
        sa.ForeignKeyConstraint(["post_id"], ["posts.id"], name=op.f("fk_reports_post_id_posts")),
        sa.ForeignKeyConstraint(
            ["reporter_id"], ["users.id"], name=op.f("fk_reports_reporter_id_users")
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_reports_user_id_users")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_reports")),
    )
    with op.batch_alter_table("reports", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_reports_post_id"), ["post_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_reports_reporter_id"), ["reporter_id"], unique=False)
        batch_op.create_index("ix_reports_resolved_at", ["resolved_at"], unique=False)
        batch_op.create_index(batch_op.f("ix_reports_user_id"), ["user_id"], unique=False)

    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(sa.Column("banned_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_column("banned_at")

    with op.batch_alter_table("reports", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_reports_user_id"))
        batch_op.drop_index("ix_reports_resolved_at")
        batch_op.drop_index(batch_op.f("ix_reports_reporter_id"))
        batch_op.drop_index(batch_op.f("ix_reports_post_id"))

    op.drop_table("reports")
