"""Fix mapping table primary keys.

Revision ID: 076bbed37e2b
Revises: 5c83ec09a61a
Create Date: 2020-07-14 23:37:42.303054+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '076bbed37e2b'
down_revision = '5c83ec09a61a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('release_code_mapping', 'release',
               existing_type=sa.INTEGER(),
               nullable=True,
               schema='cpt')
    op.alter_column('release_pla_code_mapping', 'release',
               existing_type=sa.INTEGER(),
               nullable=True,
               schema='cpt')

    op.drop_table('manufacturer_pla_code_mapping', schema='cpt')
    op.drop_table('lab_pla_code_mapping', schema='cpt')

    op.create_table('manufacturer_pla_code_mapping',
    sa.Column('manufacturer', sa.Integer(), nullable=False),
    sa.Column('code', sa.String(length=5), nullable=False),
    sa.ForeignKeyConstraint(['code'], ['cpt.pla_code.code'], name=op.f('fk_manufacturer_pla_code_mapping_code_pla_code')),
    sa.ForeignKeyConstraint(['manufacturer'], ['cpt.manufacturer.id'], name=op.f('fk_manufacturer_pla_code_mapping_manufacturer_manufacturer')),
    sa.PrimaryKeyConstraint('code', name=op.f('pk_manufacturer_pla_code_mapping')),
    schema='cpt'
    )
    op.create_table('lab_pla_code_mapping',
    sa.Column('lab', sa.Integer(), nullable=False),
    sa.Column('code', sa.String(length=5), nullable=False),
    sa.ForeignKeyConstraint(['code'], ['cpt.pla_code.code'], name=op.f('fk_lab_pla_code_mapping_code_pla_code')),
    sa.ForeignKeyConstraint(['lab'], ['cpt.lab.id'], name=op.f('fk_lab_pla_code_mapping_lab_lab')),
    sa.PrimaryKeyConstraint('code', name=op.f('pk_lab_pla_code_mapping')),
    schema='cpt'
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('release_pla_code_mapping', 'release',
               existing_type=sa.INTEGER(),
               nullable=False,
               schema='cpt')
    op.alter_column('release_code_mapping', 'release',
               existing_type=sa.INTEGER(),
               nullable=False,
               schema='cpt')

    op.drop_table('manufacturer_pla_code_mapping', schema='cpt')
    op.drop_table('lab_pla_code_mapping', schema='cpt')

    op.create_table('manufacturer_pla_code_mapping',
    sa.Column('manufacturer', sa.Integer(), nullable=False),
    sa.Column('code', sa.String(length=5), nullable=False),
    sa.ForeignKeyConstraint(['code'], ['cpt.pla_code.code'], name=op.f('fk_manufacturer_pla_code_mapping_code_pla_code')),
    sa.ForeignKeyConstraint(['manufacturer'], ['cpt.manufacturer.id'], name=op.f('fk_manufacturer_pla_code_mapping_manufacturer_manufacturer')),
    sa.PrimaryKeyConstraint('manufacturer', name=op.f('pk_manufacturer_pla_code_mapping')),
    schema='cpt'
    )
    op.create_table('lab_pla_code_mapping',
    sa.Column('lab', sa.Integer(), nullable=False),
    sa.Column('code', sa.String(length=5), nullable=False),
    sa.ForeignKeyConstraint(['code'], ['cpt.pla_code.code'], name=op.f('fk_lab_pla_code_mapping_code_pla_code')),
    sa.ForeignKeyConstraint(['lab'], ['cpt.lab.id'], name=op.f('fk_lab_pla_code_mapping_lab_lab')),
    sa.PrimaryKeyConstraint('lab', name=op.f('pk_lab_pla_code_mapping')),
    schema='cpt'
    )
    # ### end Alembic commands ###
