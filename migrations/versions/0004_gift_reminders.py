"""gift reminders

Revision ID: 0004
Revises: 0003
Create Date: 2026-10-30 19:19:42.867516

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("donations", schema=None) as batch_op:
        batch_op.add_column(sa.Column("reminded_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("donations", schema=None) as batch_op:
        batch_op.drop_column("reminded_at")
