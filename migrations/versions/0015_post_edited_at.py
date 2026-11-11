"""post edited_at

Revision ID: 0015
Revises: 0014
Create Date: 2026-11-09 21:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0015"
down_revision = "0014"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("posts", schema=None) as batch_op:
        batch_op.add_column(sa.Column("edited_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("posts", schema=None) as batch_op:
        batch_op.drop_column("edited_at")
