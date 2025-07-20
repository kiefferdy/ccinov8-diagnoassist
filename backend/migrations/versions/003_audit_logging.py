"""Add audit logging tables

Revision ID: 003
Revises: 002
Create Date: 2025-07-20 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    # Create audit_logs table for tracking changes
    op.create_table('audit_logs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('table_name', sa.String(), nullable=False),
        sa.Column('record_id', sa.String(), nullable=False),
        sa.Column('action', sa.String(), nullable=False),  # CREATE, UPDATE, DELETE
        sa.Column('old_values', sa.JSON(), nullable=True),
        sa.Column('new_values', sa.JSON(), nullable=True),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('ip_address', sa.String(), nullable=True),
        sa.Column('user_agent', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audit_logs_table_name'), 'audit_logs', ['table_name'], unique=False)
    op.create_index(op.f('ix_audit_logs_record_id'), 'audit_logs', ['record_id'], unique=False)
    op.create_index(op.f('ix_audit_logs_action'), 'audit_logs', ['action'], unique=False)
    op.create_index(op.f('ix_audit_logs_user_id'), 'audit_logs', ['user_id'], unique=False)
    op.create_index(op.f('ix_audit_logs_timestamp'), 'audit_logs', ['timestamp'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_audit_logs_timestamp'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_user_id'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_action'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_record_id'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_table_name'), table_name='audit_logs')
    op.drop_table('audit_logs')

