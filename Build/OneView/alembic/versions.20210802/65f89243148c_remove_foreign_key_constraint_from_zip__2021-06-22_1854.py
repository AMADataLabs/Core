"""Remove foreign key constraint from zip code table

Revision ID: 65f89243148c
Revises: 792d965b661c
Create Date: 2021-06-22 18:54:36.024986+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '65f89243148c'
down_revision = '792d965b661c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('fk_zip_code_metropolitan_statistical_area_metropolitan__dd1b', 'zip_code', schema='oneview', type_='foreignkey')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key('fk_zip_code_metropolitan_statistical_area_metropolitan__dd1b', 'zip_code', 'metropolitan_statistical_area', ['metropolitan_statistical_area'], ['code'], source_schema='oneview', referent_schema='oneview')
    # ### end Alembic commands ###