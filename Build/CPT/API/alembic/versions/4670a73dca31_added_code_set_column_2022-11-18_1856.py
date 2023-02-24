"""Added code_set column

Revision ID: 4670a73dca31
Revises: 4db0eadc15fd
Create Date: 2022-11-18 18:56:21.332031+00:00

"""
from   alembic import op
import sqlalchemy as sa
from   sqlalchemy.sql import text


# revision identifiers, used by Alembic.
revision = '4670a73dca31'
down_revision = '4db0eadc15fd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('release', sa.Column('code_set', sa.Integer(), nullable=True), schema='cpt')

    op.get_bind().execute(text("UPDATE cpt.release SET code_set=0"))

    op.alter_column('release', 'code_set',
               existing_type=sa.INTEGER(),
               nullable=False,
               schema='cpt')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('release', 'code_set', schema='cpt')
    # ### end Alembic commands ###
