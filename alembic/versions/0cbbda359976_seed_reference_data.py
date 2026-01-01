"""seed_reference_data

Revision ID: 0cbbda359976
Revises: e2746ef4e845
Create Date: 2026-01-01 00:38:23.693285

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0cbbda359976'
down_revision: Union[str, None] = 'e2746ef4e845'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
