"""post photo

Revision ID: 0014
Revises: 0012
Create Date: 2026-11-09 23:30:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0014"
down_revision = "0012"
branch_labels = None
depends_on = None

OLD_REASONS = "reason IN ('scam', 'business', 'harassment', 'private_info', 'spam', 'other')"
NEW_REASONS = (
    "reason IN ('scam', 'business', 'harassment', 'private_info', 'spam', 'photo', 'other')"
)


def upgrade() -> None:
    # One optional photo per post, stored outside the database (ADR 0015).
    with op.batch_alter_table("posts", schema=None) as batch_op:
        batch_op.add_column(sa.Column("photo_key", sa.String(length=80), nullable=True))
    with op.batch_alter_table("reports", schema=None) as batch_op:
        batch_op.drop_constraint("report_reason", type_="check")
        batch_op.create_check_constraint("report_reason", NEW_REASONS)


def downgrade() -> None:
    op.execute("UPDATE reports SET reason = 'other' WHERE reason = 'photo'")
    with op.batch_alter_table("reports", schema=None) as batch_op:
        batch_op.drop_constraint("report_reason", type_="check")
        batch_op.create_check_constraint("report_reason", OLD_REASONS)
    with op.batch_alter_table("posts", schema=None) as batch_op:
        batch_op.drop_column("photo_key")
