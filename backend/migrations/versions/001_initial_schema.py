"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2025-07-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create patients table
    op.create_table('patients',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('first_name', sa.String(), nullable=False),
        sa.Column('last_name', sa.String(), nullable=False),
        sa.Column('date_of_birth', sa.Date(), nullable=False),
        sa.Column('gender', sa.String(), nullable=False),
        sa.Column('contact_info', sa.JSON(), nullable=True),
        sa.Column('medical_history', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_patients_last_name'), 'patients', ['last_name'], unique=False)
    op.create_index(op.f('ix_patients_date_of_birth'), 'patients', ['date_of_birth'], unique=False)
    
    # Create episodes table
    op.create_table('episodes',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('patient_id', sa.String(), nullable=False),
        sa.Column('chief_complaint', sa.String(), nullable=True),
        sa.Column('start_date', sa.DateTime(), nullable=True),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('clinical_data', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_episodes_patient_id'), 'episodes', ['patient_id'], unique=False)
    op.create_index(op.f('ix_episodes_start_date'), 'episodes', ['start_date'], unique=False)
    op.create_index(op.f('ix_episodes_status'), 'episodes', ['status'], unique=False)
    
    # Create diagnoses table
    op.create_table('diagnoses',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('episode_id', sa.String(), nullable=False),
        sa.Column('differential_diagnoses', sa.JSON(), nullable=True),
        sa.Column('final_diagnosis', sa.String(), nullable=True),
        sa.Column('confidence_scores', sa.JSON(), nullable=True),
        sa.Column('ai_analysis_data', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['episode_id'], ['episodes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_diagnoses_episode_id'), 'diagnoses', ['episode_id'], unique=False)
    
    # Create treatments table
    op.create_table('treatments',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('episode_id', sa.String(), nullable=False),
        sa.Column('diagnosis_id', sa.String(), nullable=True),
        sa.Column('treatment_plan', sa.JSON(), nullable=True),
        sa.Column('medications', sa.JSON(), nullable=True),
        sa.Column('follow_up_instructions', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['diagnosis_id'], ['diagnoses.id'], ),
        sa.ForeignKeyConstraint(['episode_id'], ['episodes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_treatments_episode_id'), 'treatments', ['episode_id'], unique=False)
    op.create_index(op.f('ix_treatments_diagnosis_id'), 'treatments', ['diagnosis_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_treatments_diagnosis_id'), table_name='treatments')
    op.drop_index(op.f('ix_treatments_episode_id'), table_name='treatments')
    op.drop_table('treatments')
    op.drop_index(op.f('ix_diagnoses_episode_id'), table_name='diagnoses')
    op.drop_table('diagnoses')
    op.drop_index(op.f('ix_episodes_status'), table_name='episodes')
    op.drop_index(op.f('ix_episodes_start_date'), table_name='episodes')
    op.drop_index(op.f('ix_episodes_patient_id'), table_name='episodes')
    op.drop_table('episodes')
    op.drop_index(op.f('ix_patients_date_of_birth'), table_name='patients')
    op.drop_index(op.f('ix_patients_last_name'), table_name='patients')
    op.drop_table('patients')
