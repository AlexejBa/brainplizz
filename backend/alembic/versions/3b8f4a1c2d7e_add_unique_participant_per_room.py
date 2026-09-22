"""Add unique participant per room

Revision ID: 3b8f4a1c2d7e
Revises: d29fd1221ee2
Create Date: 2026-09-22 20:09:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "3b8f4a1c2d7e"
down_revision: Union[str, Sequence[str], None] = "d29fd1221ee2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_unique_constraint(
        "uq_game_participant_user_room",
        "game_participants",
        ["user_id", "room_id"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "uq_game_participant_user_room",
        "game_participants",
        type_="unique",
    )
