"""gifts seen at

Revision ID: 0018
Revises: 0017
Create Date: 2026-11-18 12:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0018"
down_revision = "0017"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # The one-time "confirmed your gift" banner shows what changed since this (#80).
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(sa.Column("gifts_seen_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_column("gifts_seen_at")
