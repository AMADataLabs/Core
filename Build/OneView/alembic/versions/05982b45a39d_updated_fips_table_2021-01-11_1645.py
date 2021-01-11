"""Updated FIPS table

Revision ID: 05982b45a39d
Revises: 73acfb36c342
Create Date: 2021-01-11 16:45:00.690658+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '05982b45a39d'
down_revision = '73acfb36c342'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('federal_information_processing_standard_county', sa.Column('county', sa.String(), nullable=False), schema='oneview')
    op.add_column('federal_information_processing_standard_county', sa.Column('state', sa.String(), nullable=False), schema='oneview')
    op.drop_column('federal_information_processing_standard_county', 'id', schema='oneview')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('federal_information_processing_standard_county', sa.Column('id', sa.VARCHAR(), autoincrement=False, nullable=False), schema='oneview')
    op.drop_column('federal_information_processing_standard_county', 'state', schema='oneview')
    op.drop_column('federal_information_processing_standard_county', 'county', schema='oneview')
    # ### end Alembic commands ###
