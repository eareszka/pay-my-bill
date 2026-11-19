"""user bio

Revision ID: 0024
Revises: 0023
Create Date: 2026-11-19 09:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0024"
down_revision = "0023"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # A short bio on the poster card of the post sheet (#282).
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(sa.Column("bio", sa.String(length=300), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("bio")
