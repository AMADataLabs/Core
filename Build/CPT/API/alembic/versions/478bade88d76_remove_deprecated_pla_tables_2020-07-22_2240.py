"""Remove deprecated PLA tables.

Revision ID: 478bade88d76
Revises: f01872aac673
Create Date: 2020-07-22 22:40:12.064526+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '478bade88d76'
down_revision = 'f01872aac673'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('pla_short_descriptor', schema='cpt')
    op.drop_table('pla_medium_descriptor', schema='cpt')
    op.drop_table('pla_long_descriptor', schema='cpt')
    op.drop_table('release_pla_code_mapping', schema='cpt')
    op.drop_table('pla_code', schema='cpt')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('pla_long_descriptor',
    sa.Column('code', sa.VARCHAR(length=5), autoincrement=False, nullable=False),
    sa.Column('descriptor', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('deleted', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('modified_date', sa.DATE(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['code'], ['cpt.pla_code.code'], name='fk_pla_long_descriptor_code_pla_code'),
    sa.PrimaryKeyConstraint('code', name='pk_pla_long_descriptor'),
    schema='cpt'
    )
    op.create_table('release_pla_code_mapping',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('cpt.release_pla_code_mapping_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('release', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('code', sa.VARCHAR(length=5), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['code'], ['cpt.pla_code.code'], name='fk_release_pla_code_mapping_code_code'),
    sa.ForeignKeyConstraint(['release'], ['cpt.release.id'], name='fk_release_pla_code_mapping_release_release'),
    sa.PrimaryKeyConstraint('id', name='pk_release_pla_code_mapping'),
    schema='cpt'
    )
    op.create_table('pla_short_descriptor',
    sa.Column('code', sa.VARCHAR(length=5), autoincrement=False, nullable=False),
    sa.Column('descriptor', sa.VARCHAR(length=28), autoincrement=False, nullable=False),
    sa.Column('deleted', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('modified_date', sa.DATE(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['code'], ['cpt.pla_code.code'], name='fk_pla_short_descriptor_code_pla_code'),
    sa.PrimaryKeyConstraint('code', name='pk_pla_short_descriptor'),
    schema='cpt'
    )
    op.create_table('pla_code',
    sa.Column('code', sa.VARCHAR(length=5), autoincrement=False, nullable=False),
    sa.Column('status', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('test_name', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('deleted', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('modified_date', sa.DATE(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('code', name='pk_pla_code'),
    schema='cpt',
    postgresql_ignore_search_path=False
    )
    op.create_table('pla_medium_descriptor',
    sa.Column('code', sa.VARCHAR(length=5), autoincrement=False, nullable=False),
    sa.Column('descriptor', sa.VARCHAR(length=48), autoincrement=False, nullable=False),
    sa.Column('deleted', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('modified_date', sa.DATE(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['code'], ['cpt.pla_code.code'], name='fk_pla_medium_descriptor_code_pla_code'),
    sa.PrimaryKeyConstraint('code', name='pk_pla_medium_descriptor'),
    schema='cpt'
    )
    # ### end Alembic commands ###
