"""Fix foreign key for historical resident

Revision ID: 18430bb4b902
Revises: 2998c8894a49
Create Date: 2021-10-06 14:43:48.922105+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '18430bb4b902'
down_revision = '2998c8894a49'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('historical_resident', 'medical_education_number', schema='oneview')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('historical_resident', sa.Column('medical_education_number', sa.VARCHAR(), autoincrement=False, nullable=False), schema='oneview')
    # ### end Alembic commands ###