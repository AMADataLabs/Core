"""Remove unique constraint on release column of the release code mapping table.

Revision ID: 5c83ec09a61a
Revises: c52511ce9623
Create Date: 2020-06-24 21:23:48.579811+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5c83ec09a61a'
down_revision = 'c52511ce9623'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table('release_code_mapping', schema='cpt')

    op.create_table('release_code_mapping',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('release', sa.Integer(), nullable=False),
    sa.Column('code', sa.String(length=5), nullable=False),
    sa.ForeignKeyConstraint(['code'], ['cpt.code.code'], name=op.f('fk_release_code_mapping_code_code')),
    sa.ForeignKeyConstraint(['release'], ['cpt.release.id'], name=op.f('fk_release_code_mapping_release_release')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_release_code_mapping')),
    schema='cpt'
    )



def downgrade():
    op.drop_table('release_code_mapping', schema='cpt')

    op.create_table('release_code_mapping',
    sa.Column('release', sa.Integer(), nullable=False),
    sa.Column('code', sa.String(length=5), nullable=False),
    sa.ForeignKeyConstraint(['code'], ['cpt.code.code'], name=op.f('fk_release_code_mapping_code_code')),
    sa.ForeignKeyConstraint(['release'], ['cpt.release.id'], name=op.f('fk_release_code_mapping_release_release')),
    sa.PrimaryKeyConstraint('release', name=op.f('pk_release_code_mapping')),
    schema='cpt'
    )
