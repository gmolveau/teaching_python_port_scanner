"""add_scan_model

Revision ID: 2622eb2bb294
Revises: b4c2fdc5c32f
Create Date: 2026-03-30 11:28:42.294779

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2622eb2bb294"
down_revision: Union[str, Sequence[str], None] = "b4c2fdc5c32f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "scans",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("ip_target", sa.String(), nullable=False),
        sa.Column("port_target", sa.Integer(), nullable=False),
        sa.Column("result", sa.String(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("sessions") as batch_op:
        batch_op.add_column(
            sa.Column("external_id", sa.Uuid(native_uuid=False), nullable=False)
        )
        batch_op.create_unique_constraint("uq_sessions_external_id", ["external_id"])
        batch_op.drop_column("session_id")
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(
            sa.Column(
                "created_at",
                sa.DateTime(),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=False,
            )
        )


def downgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("created_at")
    with op.batch_alter_table("sessions") as batch_op:
        batch_op.add_column(sa.Column("session_id", sa.VARCHAR(), nullable=False))
        batch_op.drop_constraint("uq_sessions_external_id", type_="unique")
        batch_op.drop_column("external_id")
    op.drop_table("scans")
