"""make username not null + unique

Revision ID: ba627698b030
Revises: 32e01c660e78
Create Date: 2026-06-11 11:12:52.130255

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ba627698b030'
down_revision: Union[str, Sequence[str], None] = '32e01c660e78'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    conn = op.get_bind()
    
    result = conn.execute(sa.text("SELECT COUNT(*) FROM users WHERE username IS NULL"))
    if result.scalar() > 0:
        raise Exception("Cannot make username NOT NULL because there are existing records with NULL values.")
    
    op.alter_column('users', 'username', existing_type=sa.String(length=40), nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('users', 'username', existing_type=sa.String(length=40), nullable=True)
