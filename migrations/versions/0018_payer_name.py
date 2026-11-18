"""payer name

Revision ID: 0018
Revises: 0017
Create Date: 2026-11-18 13:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0018"
down_revision = "0017"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Helps a poster match a gift to their payment app (#81).
    with op.batch_alter_table("donations", schema=None) as batch_op:
        batch_op.add_column(sa.Column("payer_name", sa.String(length=60), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("donations", schema=None) as batch_op:
        batch_op.drop_column("payer_name")
