"""add schedule table

Revision ID: 20251021_add_schedule_table
Revises: 20251012_add_department_id
Create Date: 2025-10-21 00:00:00
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20251021_add_schedule_table'
down_revision = '20251012_add_department_id'
branch_labels = None
depends_on = None


def upgrade():
    # Check if table already exists
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    if 'schedules' not in inspector.get_table_names():
        op.create_table(
            'schedules',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('staff_id', sa.Integer(), nullable=False),
            sa.Column('day_of_week', sa.Integer(), nullable=False),
            sa.Column('start_time', sa.String(), nullable=False),
            sa.Column('end_time', sa.String(), nullable=False),
            sa.Column('is_available', sa.Boolean(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['staff_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_schedules_id'), 'schedules', ['id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_schedules_id'), table_name='schedules')
    op.drop_table('schedules')
