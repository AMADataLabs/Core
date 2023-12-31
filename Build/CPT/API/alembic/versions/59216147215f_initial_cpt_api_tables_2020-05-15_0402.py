"""Initial CPT API tables.

Revision ID: 59216147215f
Revises: 
Create Date: 2020-05-15 04:02:00.017216+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '59216147215f'
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
    op.create_table('code',
    sa.Column('code', sa.String(length=5), nullable=False),
    sa.PrimaryKeyConstraint('code', name=op.f('pk_code')),
    schema='cpt'
    )
    op.create_table('modifier_type',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=20), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_modifier_type')),
    schema='cpt'
    )
    op.create_table('release_type',
    sa.Column('type', sa.String(length=3), nullable=False),
    sa.PrimaryKeyConstraint('type', name=op.f('pk_release_type')),
    schema='cpt'
    )
    op.create_table('clinician_descriptor_code_mapping',
    sa.Column('clinician_descriptor', sa.Integer(), nullable=False),
    sa.Column('code', sa.String(length=5), nullable=False),
    sa.ForeignKeyConstraint(['clinician_descriptor'], ['cpt.clinician_descriptor.id'], name=op.f('fk_clinician_descriptor_code_mapping_clinician_descriptor_clinician_descriptor')),
    sa.ForeignKeyConstraint(['code'], ['cpt.code.code'], name=op.f('fk_clinician_descriptor_code_mapping_code_code')),
    sa.PrimaryKeyConstraint('clinician_descriptor', name=op.f('pk_clinician_descriptor_code_mapping')),
    schema='cpt'
    )
    op.create_table('concept',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('cpt_code', sa.String(length=5), nullable=False),
    sa.ForeignKeyConstraint(['cpt_code'], ['cpt.code.code'], name=op.f('fk_concept_cpt_code_code')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_concept')),
    schema='cpt'
    )
    op.create_table('consumer_descriptor',
    sa.Column('code', sa.String(length=5), nullable=False),
    sa.Column('descriptor', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['code'], ['cpt.code.code'], name=op.f('fk_consumer_descriptor_code_code')),
    sa.PrimaryKeyConstraint('code', name=op.f('pk_consumer_descriptor')),
    schema='cpt'
    )
    op.create_table('long_descriptor',
    sa.Column('code', sa.String(length=5), nullable=False),
    sa.Column('descriptor', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['code'], ['cpt.code.code'], name=op.f('fk_long_descriptor_code_code')),
    sa.PrimaryKeyConstraint('code', name=op.f('pk_long_descriptor')),
    schema='cpt'
    )
    op.create_table('medium_descriptor',
    sa.Column('code', sa.String(length=5), nullable=False),
    sa.Column('descriptor', sa.String(length=48), nullable=False),
    sa.ForeignKeyConstraint(['code'], ['cpt.code.code'], name=op.f('fk_medium_descriptor_code_code')),
    sa.PrimaryKeyConstraint('code', name=op.f('pk_medium_descriptor')),
    schema='cpt'
    )
    op.create_table('modifier',
    sa.Column('modifier', sa.String(length=2), nullable=False),
    sa.Column('type', sa.Integer(), nullable=False),
    sa.Column('descriptor', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['type'], ['cpt.modifier_type.id'], name=op.f('fk_modifier_type_modifier_type')),
    sa.PrimaryKeyConstraint('modifier', name=op.f('pk_modifier')),
    schema='cpt'
    )
    op.create_table('release',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('type', sa.String(length=3), nullable=False),
    sa.ForeignKeyConstraint(['type'], ['cpt.release_type.type'], name=op.f('fk_release_type_release_type')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_release')),
    schema='cpt'
    )
    op.create_table('short_descriptor',
    sa.Column('code', sa.String(length=5), nullable=False),
    sa.Column('descriptor', sa.String(length=28), nullable=False),
    sa.ForeignKeyConstraint(['code'], ['cpt.code.code'], name=op.f('fk_short_descriptor_code_code')),
    sa.PrimaryKeyConstraint('code', name=op.f('pk_short_descriptor')),
    schema='cpt'
    )
    op.create_table('release_code_mapping',
    sa.Column('release', sa.Integer(), nullable=False),
    sa.Column('code', sa.String(length=5), nullable=False),
    sa.ForeignKeyConstraint(['code'], ['cpt.code.code'], name=op.f('fk_release_code_mapping_code_code')),
    sa.ForeignKeyConstraint(['release'], ['cpt.release.id'], name=op.f('fk_release_code_mapping_release_release')),
    sa.PrimaryKeyConstraint('release', name=op.f('pk_release_code_mapping')),
    schema='cpt'
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('release_code_mapping', schema='cpt')
    op.drop_table('short_descriptor', schema='cpt')
    op.drop_table('release', schema='cpt')
    op.drop_table('modifier', schema='cpt')
    op.drop_table('medium_descriptor', schema='cpt')
    op.drop_table('long_descriptor', schema='cpt')
    op.drop_table('consumer_descriptor', schema='cpt')
    op.drop_table('concept', schema='cpt')
    op.drop_table('clinician_descriptor_code_mapping', schema='cpt')
    op.drop_table('release_type', schema='cpt')
    op.drop_table('modifier_type', schema='cpt')
    op.drop_table('code', schema='cpt')
    op.drop_table('clinician_descriptor', schema='cpt')
    # ### end Alembic commands ###
