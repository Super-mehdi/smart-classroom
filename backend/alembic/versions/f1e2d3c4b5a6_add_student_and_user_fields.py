"""add student and user fields

Revision ID: f1e2d3c4b5a6
Revises: b35ebe85c878
Create Date: 2026-05-19 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f1e2d3c4b5a6'
down_revision: Union[str, Sequence[str], None] = 'b35ebe85c878'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add missing columns to users (defensively with IF NOT EXISTS)
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS department VARCHAR")
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS office_number VARCHAR")
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_online BOOLEAN DEFAULT FALSE")
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS last_seen TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()")

    # 2. Create students table (defensively)
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()
    if 'students' not in tables:
        op.create_table('students',
            sa.Column('id', sa.String(), nullable=False),
            sa.Column('name', sa.String(), nullable=False),
            sa.Column('photo_path', sa.String(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_students_id'), 'students', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_students_id'), table_name='students')
    op.drop_table('students')
    op.drop_column('users', 'is_online')
    op.drop_column('users', 'office_number')
    op.drop_column('users', 'department')
