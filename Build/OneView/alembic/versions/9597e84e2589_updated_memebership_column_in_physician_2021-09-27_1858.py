"""Updated memebership column in physician

Revision ID: 9597e84e2589
Revises: 046381fb7335
Create Date: 2021-09-27 18:58:31.815929+00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text as sql_text

# revision identifiers, used by Alembic.
revision = '9597e84e2589'
down_revision = '046381fb7335'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('physician', sa.Column('membership_status', sa.String(), nullable=True), schema='oneview')
    op.drop_column('physician', 'membership_year', schema='oneview')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('physician', sa.Column('membership_year', sa.VARCHAR(), autoincrement=False, nullable=True), schema='oneview')
    op.drop_column('physician', 'membership_status', schema='oneview')
    # ### end Alembic commands ###
