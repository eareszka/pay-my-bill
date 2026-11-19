"""more post photos

Revision ID: 0023
Revises: 0022
Create Date: 2026-11-18 21:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0023"
down_revision = "0022"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Up to four photos after the cover (#279, ADR 0020).
    with op.batch_alter_table("posts") as batch_op:
        batch_op.add_column(
            sa.Column("more_photo_keys", sa.JSON(), server_default="[]", nullable=False)
        )


def downgrade() -> None:
    with op.batch_alter_table("posts") as batch_op:
        batch_op.drop_column("more_photo_keys")
