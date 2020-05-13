"""Initial CPT table.

Revision ID: fdf9036e6d91
Revises: 
Create Date: 2020-05-13 22:32:50.491852+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fdf9036e6d91'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('clinician_descriptor',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('descriptor', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_clinician_descriptor')),
    schema='cpt'
    )
    op.create_table('consumer_descriptor',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('descriptor', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_consumer_descriptor')),
    schema='cpt'
    )
    op.create_table('cpt_descriptor',
    sa.Column('cpt_code', sa.String(length=5), nullable=False),
    sa.Column('short_form', sa.String(length=28), nullable=False),
    sa.Column('medium_form', sa.String(length=48), nullable=False),
    sa.Column('long_form', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('cpt_code', name=op.f('pk_cpt_descriptor')),
    schema='cpt'
    )
    op.create_table('modifier_type',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=20), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_modifier_type')),
    schema='cpt'
    )
    op.create_table('concept',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('cpt_code', sa.String(length=5), nullable=False),
    sa.Column('consumer_descriptor_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['consumer_descriptor_id'], ['cpt.consumer_descriptor.id'], name=op.f('fk_concept_consumer_descriptor_id_consumer_descriptor')),
    sa.ForeignKeyConstraint(['cpt_code'], ['cpt.cpt_descriptor.cpt_code'], name=op.f('fk_concept_cpt_code_cpt_descriptor')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_concept')),
    schema='cpt'
    )
    op.create_table('modifier',
    sa.Column('mod_code', sa.String(length=2), nullable=False),
    sa.Column('type_id', sa.Integer(), nullable=False),
    sa.Column('description', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['type_id'], ['cpt.modifier_type.id'], name=op.f('fk_modifier_type_id_modifier_type')),
    sa.PrimaryKeyConstraint('mod_code', name=op.f('pk_modifier')),
    schema='cpt'
    )
    op.create_table('clinician_descriptor_mapping',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('clinician_descriptor_id', sa.Integer(), nullable=False),
    sa.Column('concept_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['clinician_descriptor_id'], ['cpt.clinician_descriptor.id'], name=op.f('fk_clinician_descriptor_mapping_clinician_descriptor_id_clinician_descriptor')),
    sa.ForeignKeyConstraint(['concept_id'], ['cpt.concept.id'], name=op.f('fk_clinician_descriptor_mapping_concept_id_concept')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_clinician_descriptor_mapping')),
    schema='cpt'
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('clinician_descriptor_mapping', schema='cpt')
    op.drop_table('modifier', schema='cpt')
    op.drop_table('concept', schema='cpt')
    op.drop_table('modifier_type', schema='cpt')
    op.drop_table('cpt_descriptor', schema='cpt')
    op.drop_table('consumer_descriptor', schema='cpt')
    op.drop_table('clinician_descriptor', schema='cpt')
    # ### end Alembic commands ###
