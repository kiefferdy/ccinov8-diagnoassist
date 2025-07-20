"""Add FHIR resources table

Revision ID: 002
Revises: 001
Create Date: 2025-07-20 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # Create fhir_resources table for storing FHIR data
    op.create_table('fhir_resources',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('resource_type', sa.String(), nullable=False),
        sa.Column('resource_id', sa.String(), nullable=False),
        sa.Column('version_id', sa.String(), nullable=True),
        sa.Column('fhir_data', sa.JSON(), nullable=False),
        sa.Column('internal_id', sa.String(), nullable=True),  # Link to internal tables
        sa.Column('last_updated', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('resource_type', 'resource_id', 'version_id', name='uq_fhir_resource_version')
    )
    op.create_index(op.f('ix_fhir_resources_resource_type'), 'fhir_resources', ['resource_type'], unique=False)
    op.create_index(op.f('ix_fhir_resources_resource_id'), 'fhir_resources', ['resource_id'], unique=False)
    op.create_index(op.f('ix_fhir_resources_internal_id'), 'fhir_resources', ['internal_id'], unique=False)
    op.create_index(op.f('ix_fhir_resources_last_updated'), 'fhir_resources', ['last_updated'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_fhir_resources_last_updated'), table_name='fhir_resources')
    op.drop_index(op.f('ix_fhir_resources_internal_id'), table_name='fhir_resources')
    op.drop_index(op.f('ix_fhir_resources_resource_id'), table_name='fhir_resources')
    op.drop_index(op.f('ix_fhir_resources_resource_type'), table_name='fhir_resources')
    op.drop_table('fhir_resources')
