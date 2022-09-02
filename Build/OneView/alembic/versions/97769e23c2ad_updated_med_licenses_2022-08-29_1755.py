"""Updated med licenses

Revision ID: 97769e23c2ad
Revises: 3452d1f6f846
Create Date: 2022-08-29 17:55:49.699825+00:00

"""
from alembic import op
import sqlalchemy as sa
from alembic_utils.pg_trigger import PGTrigger
from sqlalchemy import text as sql_text
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '97769e23c2ad'
down_revision = '3452d1f6f846'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('medical_license', 'renew_date', schema='oneview')
    op.drop_column('medical_license', 'expiry_date', schema='oneview')
    op.drop_column('medical_license', 'issue_date', schema='oneview')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('medical_license', sa.Column('issue_date', sa.VARCHAR(), autoincrement=False, nullable=True), schema='oneview')
    op.add_column('medical_license', sa.Column('expiry_date', sa.VARCHAR(), autoincrement=False, nullable=True), schema='oneview')
    op.add_column('medical_license', sa.Column('renew_date', sa.VARCHAR(), autoincrement=False, nullable=True), schema='oneview')
    # ### end Alembic commands ###
