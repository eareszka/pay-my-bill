"""update photo

Revision ID: 0025
Revises: 0024
Create Date: 2026-11-19 15:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0025"
down_revision = "0024"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # An optional photo on the results update (#69).
    with op.batch_alter_table("posts") as batch_op:
        batch_op.add_column(sa.Column("update_photo_key", sa.String(length=80), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("posts") as batch_op:
        batch_op.drop_column("update_photo_key")
