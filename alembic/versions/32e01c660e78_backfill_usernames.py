"""backfill usernames

Revision ID: 32e01c660e78
Revises: 8f15255e8711
Create Date: 2026-06-11 11:07:06.446814

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '32e01c660e78'
down_revision: Union[str, Sequence[str], None] = '8f15255e8711'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    conn = op.get_bind()
    result = conn.execute(sa.text("SELECT id, email FROM users"))
    
    seen = set()
    for user_id, email in result:
        base_username = email.split("@")[0].lower()
        username = base_username
        suffix = 1
        
        # Ensure uniqueness of the username
        while username in seen:
            username = f"{base_username}_{suffix}"
            suffix += 1
        
        seen.add(username)
        
        conn.execute(sa.text("UPDATE users SET username = :username WHERE id = :user_id"), {"username": username, "user_id": user_id})


def downgrade() -> None:
    """Downgrade schema."""
    conn = op.get_bind()
    conn.execute(sa.text("UPDATE users SET username = NULL"))
