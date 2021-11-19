"""Remove non null constraint

Revision ID: cc69ba186fff
Revises: 9a3a2bc5bdeb
Create Date: 2021-11-18 21:18:42.888811+00:00

"""
from alembic import op
import sqlalchemy as sa
from alembic_utils.pg_materialized_view import PGMaterializedView
from sqlalchemy import text as sql_text

# revision identifiers, used by Alembic.
revision = 'cc69ba186fff'
down_revision = '9a3a2bc5bdeb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('business', 'iqvia_address_id',
               existing_type=sa.VARCHAR(),
               nullable=False,
               schema='oneview')
    op.alter_column('business', 'physical_address_1',
               existing_type=sa.VARCHAR(),
               nullable=False,
               schema='oneview')
    op.alter_column('business', 'physical_city',
               existing_type=sa.VARCHAR(),
               nullable=False,
               schema='oneview')
    op.alter_column('business', 'physical_state',
               existing_type=sa.VARCHAR(),
               nullable=False,
               schema='oneview')
    op.alter_column('business', 'physical_zipcode',
               existing_type=sa.VARCHAR(),
               nullable=False,
               schema='oneview')
    op.alter_column('business', 'postal_address_1',
               existing_type=sa.VARCHAR(),
               nullable=False,
               schema='oneview')
    op.alter_column('business', 'postal_city',
               existing_type=sa.VARCHAR(),
               nullable=False,
               schema='oneview')
    op.alter_column('business', 'postal_state',
               existing_type=sa.VARCHAR(),
               nullable=False,
               schema='oneview')
    op.alter_column('business', 'postal_zipcode',
               existing_type=sa.VARCHAR(),
               nullable=False,
               schema='oneview')
    op.alter_column('business', 'primary_class_of_trade',
               existing_type=sa.VARCHAR(),
               nullable=False,
               schema='oneview')
    op.alter_column('business', 'record_type',
               existing_type=sa.VARCHAR(),
               nullable=False,
               schema='oneview')
    op.alter_column('business', 'status_indicator',
               existing_type=sa.VARCHAR(),
               nullable=False,
               schema='oneview')
    op.alter_column('credentialing_customer', 'category',
               existing_type=sa.VARCHAR(),
               nullable=True,
               schema='oneview')
    op.alter_column('credentialing_customer', 'category_description',
               existing_type=sa.VARCHAR(),
               nullable=True,
               schema='oneview')
    op.alter_column('credentialing_customer', 'address_1',
               existing_type=sa.VARCHAR(),
               nullable=True,
               schema='oneview')
    op.alter_column('credentialing_customer', 'address_2',
               existing_type=sa.VARCHAR(),
               nullable=True,
               schema='oneview')
    op.alter_column('credentialing_customer', 'address_3',
               existing_type=sa.VARCHAR(),
               nullable=True,
               schema='oneview')
    op.alter_column('credentialing_customer', 'city',
               existing_type=sa.VARCHAR(),
               nullable=True,
               schema='oneview')
    op.alter_column('credentialing_customer', 'state',
               existing_type=sa.VARCHAR(),
               nullable=True,
               schema='oneview')
    op.alter_column('credentialing_customer', 'zipcode',
               existing_type=sa.VARCHAR(),
               nullable=True,
               schema='oneview')
    op.alter_column('credentialing_customer', 'phone_number',
               existing_type=sa.VARCHAR(),
               nullable=True,
               schema='oneview')
    op.alter_column('credentialing_customer', 'company_name',
               existing_type=sa.VARCHAR(),
               nullable=True,
               schema='oneview')
    op.alter_column('historical_resident', 'training_type',
               existing_type=sa.VARCHAR(),
               nullable=True,
               schema='oneview')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###

    op.alter_column('historical_resident', 'training_type',
               existing_type=sa.VARCHAR(),
               nullable=False,
               schema='oneview')
    op.alter_column('credentialing_customer', 'company_name',
               existing_type=sa.VARCHAR(),
               nullable=False,
               schema='oneview')
    op.alter_column('credentialing_customer', 'phone_number',
               existing_type=sa.VARCHAR(),
               nullable=False,
               schema='oneview')
    op.alter_column('credentialing_customer', 'zipcode',
               existing_type=sa.VARCHAR(),
               nullable=False,
               schema='oneview')
    op.alter_column('credentialing_customer', 'state',
               existing_type=sa.VARCHAR(),
               nullable=False,
               schema='oneview')
    op.alter_column('credentialing_customer', 'city',
               existing_type=sa.VARCHAR(),
               nullable=False,
               schema='oneview')
    op.alter_column('credentialing_customer', 'address_3',
               existing_type=sa.VARCHAR(),
               nullable=False,
               schema='oneview')
    op.alter_column('credentialing_customer', 'address_2',
               existing_type=sa.VARCHAR(),
               nullable=False,
               schema='oneview')
    op.alter_column('credentialing_customer', 'address_1',
               existing_type=sa.VARCHAR(),
               nullable=False,
               schema='oneview')
    op.alter_column('credentialing_customer', 'category_description',
               existing_type=sa.VARCHAR(),
               nullable=False,
               schema='oneview')
    op.alter_column('credentialing_customer', 'category',
               existing_type=sa.VARCHAR(),
               nullable=False,
               schema='oneview')
    op.alter_column('business', 'status_indicator',
               existing_type=sa.VARCHAR(),
               nullable=True,
               schema='oneview')
    op.alter_column('business', 'record_type',
               existing_type=sa.VARCHAR(),
               nullable=True,
               schema='oneview')
    op.alter_column('business', 'primary_class_of_trade',
               existing_type=sa.VARCHAR(),
               nullable=True,
               schema='oneview')
    op.alter_column('business', 'postal_zipcode',
               existing_type=sa.VARCHAR(),
               nullable=True,
               schema='oneview')
    op.alter_column('business', 'postal_state',
               existing_type=sa.VARCHAR(),
               nullable=True,
               schema='oneview')
    op.alter_column('business', 'postal_city',
               existing_type=sa.VARCHAR(),
               nullable=True,
               schema='oneview')
    op.alter_column('business', 'postal_address_1',
               existing_type=sa.VARCHAR(),
               nullable=True,
               schema='oneview')
    op.alter_column('business', 'physical_zipcode',
               existing_type=sa.VARCHAR(),
               nullable=True,
               schema='oneview')
    op.alter_column('business', 'physical_state',
               existing_type=sa.VARCHAR(),
               nullable=True,
               schema='oneview')
    op.alter_column('business', 'physical_city',
               existing_type=sa.VARCHAR(),
               nullable=True,
               schema='oneview')
    op.alter_column('business', 'physical_address_1',
               existing_type=sa.VARCHAR(),
               nullable=True,
               schema='oneview')
    op.alter_column('business', 'iqvia_address_id',
               existing_type=sa.VARCHAR(),
               nullable=True,
               schema='oneview')
    # ### end Alembic commands ###
