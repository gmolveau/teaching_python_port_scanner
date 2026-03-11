"""create sessions table

Revision ID: e8ba06d9eaec
Revises: 4c67b0aadecc
Create Date: 2026-02-10 21:40:40.329236

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e8ba06d9eaec"
down_revision: Union[str, Sequence[str], None] = "4c67b0aadecc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("""
        CREATE TABLE sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE NOT NULL,
            user_id INTEGER NOT NULL REFERENCES users(id),
            created_at TEXT NOT NULL,
            expires_at TEXT NOT NULL
        );
    """)


def downgrade():
    op.execute("DROP TABLE sessions")
