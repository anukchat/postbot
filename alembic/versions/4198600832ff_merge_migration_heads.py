"""stabilize alembic head

Revision ID: 4198600832ff
Revises: cf32c51cc0a1
Create Date: 2026-01-02 10:18:50.489643

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4198600832ff'
down_revision: Union[str, None] = 'cf32c51cc0a1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
