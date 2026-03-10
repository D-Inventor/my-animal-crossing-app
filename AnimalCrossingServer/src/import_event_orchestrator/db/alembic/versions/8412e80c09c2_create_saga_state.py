"""Create saga state

Revision ID: 8412e80c09c2
Revises:
Create Date: 2026-03-10 18:33:39.505455

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8412e80c09c2"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "saga_state",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column(
            "state",
            sa.Enum(
                "started", "completed", "failed", "compensating", name="sagastatus"
            ),
            nullable=False,
            server_default="started",
        ),
        sa.Column("completed_steps", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("data", sa.JSON(), nullable=False, server_default="{}"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("saga_state")
    sa.Enum(name="sagastatus").drop(op.get_bind())
