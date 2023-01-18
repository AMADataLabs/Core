"""Add uniqueness constraint to code in release code mapping table.

Revision ID: 6a5a0357459c
Revises: dd6ef3fbdbcb
Create Date: 2020-08-19 19:07:32.162161+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6a5a0357459c'
down_revision = 'dd6ef3fbdbcb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('release_code_mapping', 'release',
               existing_type=sa.INTEGER(),
               nullable=False,
               schema='cpt')
    op.create_unique_constraint(op.f('uq_release_code_mapping_code'), 'release_code_mapping', ['code'], schema='cpt')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(op.f('uq_release_code_mapping_code'), 'release_code_mapping', schema='cpt', type_='unique')
    op.alter_column('release_code_mapping', 'release',
               existing_type=sa.INTEGER(),
               nullable=True,
               schema='cpt')
    # ### end Alembic commands ###