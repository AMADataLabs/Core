"""Updated melissa data foreign key

Revision ID: d1c37baeda2b
Revises: 9597e84e2589
Create Date: 2021-09-27 20:26:19.572443+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd1c37baeda2b'
down_revision = '9597e84e2589'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('fk_zip_code_core_based_statistical_areas_core_based_sta_0ee8', 'zip_code_core_based_statistical_areas', schema='oneview', type_='foreignkey')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key('fk_zip_code_core_based_statistical_areas_core_based_sta_0ee8', 'zip_code_core_based_statistical_areas', 'core_based_statistical_area_melissa', ['core_based_statistical_area'], ['code'], source_schema='oneview', referent_schema='oneview')
    # ### end Alembic commands ###
