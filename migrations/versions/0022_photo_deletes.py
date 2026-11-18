"""photo deletes

Revision ID: 0022
Revises: 0021
Create Date: 2026-11-18 18:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0022"
down_revision = "0021"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Failed photo deletes wait here for the daily retry (#149).
    op.create_table(
        "photo_deletes",
        sa.Column("key", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("key", name=op.f("pk_photo_deletes")),
    )


def downgrade() -> None:
    op.drop_table("photo_deletes")
