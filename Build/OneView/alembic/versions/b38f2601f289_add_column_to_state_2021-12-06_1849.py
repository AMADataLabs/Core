"""Add column to state

Revision ID: b38f2601f289
Revises: 49a94da15973
Create Date: 2021-12-06 18:49:36.432799+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b38f2601f289'
down_revision = '49a94da15973'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('state', sa.Column('abbreviation', sa.String(), nullable=True), schema='oneview')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('state', 'abbreviation', schema='oneview')
    # ### end Alembic commands ###
