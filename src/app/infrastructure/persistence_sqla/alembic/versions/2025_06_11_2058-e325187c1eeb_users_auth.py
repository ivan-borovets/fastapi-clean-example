"""users,auth

Revision ID: e325187c1eeb
Revises:
Create Date: 2025-06-11 20:58:58.908948

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "e325187c1eeb"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    sa.Enum("SUPER_ADMIN", "ADMIN", "USER", name="userrole").create(op.get_bind())
    op.create_table(
        "auth_sessions",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("expiration", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_auth_sessions")),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("username", sa.String(length=20), nullable=False),
        sa.Column("password_hash", sa.LargeBinary(), nullable=False),
        sa.Column(
            "role",
            postgresql.ENUM(
                "SUPER_ADMIN", "ADMIN", "USER", name="userrole", create_type=False
            ),
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("username", name=op.f("uq_users_username")),
    )


def downgrade() -> None:
    op.drop_table("users")
    op.drop_table("auth_sessions")
    sa.Enum("SUPER_ADMIN", "ADMIN", "USER", name="userrole").drop(op.get_bind())
