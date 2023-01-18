"""Update fips table

Revision ID: d3a916b0e911
Revises: 256ef8f273b2
Create Date: 2021-06-10 19:10:47.346970+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd3a916b0e911'
down_revision = '256ef8f273b2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('federal_information_processing_standard_county', sa.Column('id', sa.String(), nullable=False), schema='oneview')
    op.drop_column('iqvia_update', 'id', schema='oneview')
    op.add_column('physician', sa.Column('entity_id', sa.String(), nullable=True), schema='oneview')
    op.add_column('physician', sa.Column('party_id', sa.String(), nullable=True), schema='oneview')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('physician', 'party_id', schema='oneview')
    op.drop_column('physician', 'entity_id', schema='oneview')
    op.add_column('iqvia_update', sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('oneview.iqvia_update_id_seq'::regclass)"), autoincrement=True, nullable=False), schema='oneview')
    op.drop_column('federal_information_processing_standard_county', 'id', schema='oneview')
    # ### end Alembic commands ###