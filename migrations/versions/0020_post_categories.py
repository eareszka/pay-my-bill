"""post categories and show less

Revision ID: 0020
Revises: 0019
Create Date: 2026-11-18 14:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0020"
down_revision = "0019"
branch_labels = None
depends_on = None

CATEGORIES = ("rent", "bills", "food", "transport", "health", "kids", "fun", "other")


def upgrade() -> None:
    # Existing posts become Other (#119).
    with op.batch_alter_table("posts", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("category", sa.String(length=20), server_default="other", nullable=False)
        )
        batch_op.create_check_constraint("post_category", f"category IN {CATEGORIES}")
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(sa.Column("show_less", sa.String(length=100), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_column("show_less")
    with op.batch_alter_table("posts", schema=None) as batch_op:
        batch_op.drop_constraint("post_category", type_="check")
        batch_op.drop_column("category")
