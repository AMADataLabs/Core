"""Adding class of trade classification table

Revision ID: 86fbc4e7fb4b
Revises: 38d10d5eee0b
Create Date: 2021-09-20 23:00:05.605594+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '86fbc4e7fb4b'
down_revision = '38d10d5eee0b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('class_of_trade_classification',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_class_of_trade_classification')),
    schema='oneview'
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('class_of_trade_classification', schema='oneview')
    # ### end Alembic commands ###