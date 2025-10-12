"""add department_id to patient_visits

Revision ID: 20251012_add_department_id
Revises: 
Create Date: 2025-10-12 12:50:00
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20251012_add_department_id'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    # only add column if it doesn't already exist
    res = conn.execute(sa.text("PRAGMA table_info('patient_visits')")).fetchall()
    cols = [r[1] for r in res]
    if 'department_id' not in cols:
        op.add_column('patient_visits', sa.Column('department_id', sa.Integer(), nullable=True))


def downgrade():
    # dropping columns in sqlite is limited; skip for downgrade
    pass
