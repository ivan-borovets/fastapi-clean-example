"""Users, Sessions

Revision ID: ca0eba589416
Revises: 
Create Date: 2024-11-03 18:39:19.744246

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "ca0eba589416"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    sa.Enum("ADMIN", "USER", name="userroleenum").create(op.get_bind())
    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("username", sa.String(length=20), nullable=False),
        sa.Column("password_hash", sa.LargeBinary(), nullable=False),
        sa.Column(
            "roles",
            sa.ARRAY(
                postgresql.ENUM("ADMIN", "USER", name="userroleenum", create_type=False)
            ),
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("username", name=op.f("uq_users_username")),
    )
    op.create_table(
        "sessions",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=True),
        sa.Column("expiration", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_sessions_user_id_users")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_sessions")),
    )


def downgrade() -> None:
    op.drop_table("sessions")
    op.drop_table("users")
    sa.Enum("ADMIN", "USER", name="userroleenum").drop(op.get_bind())
