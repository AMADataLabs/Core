"""add physical_zipcode5 to business table

Revision ID: 6bdf5e50865c
Revises: 2893c7b0bb27
Create Date: 2023-05-17 14:29:52.068604+00:00

"""
from alembic import op
import sqlalchemy as sa
from alembic_utils.pg_materialized_view import PGMaterializedView
from sqlalchemy import text as sql_text
from alembic_utils.pg_trigger import PGTrigger
from sqlalchemy import text as sql_text
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '6bdf5e50865c'
down_revision = '2893c7b0bb27'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###

    op.add_column('business', sa.Column('physical_zipcode5', sa.String(), nullable=True), schema='oneview')
    op.execute("UPDATE oneview.business b SET physical_zipcode5 = split_part(b.physical_zipcode, '-' , 1)")
    op.alter_column('business', 'physical_zipcode5', nullable=False, schema='oneview')

    op.create_index(op.f('ix_oneview_business_physical_zipcode5'), 'business', ['physical_zipcode5'], unique=False, schema='oneview')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###

    op.drop_index(op.f('ix_oneview_business_physical_zipcode5'), table_name='business', schema='oneview')

    op.drop_column('business', 'physical_zipcode5', schema='oneview')

    # ### end Alembic commands ###
