"""Temp remove iqvia fk contraimts

Revision ID: fba813690f36
Revises: 88fb1175c48d
Create Date: 2020-11-17 16:43:55.584780+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fba813690f36'
down_revision = '88fb1175c48d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('fk_provider_affiliation_business_business', 'provider_affiliation', schema='oneview', type_='foreignkey')
    op.drop_constraint('fk_provider_affiliation_provider_provider', 'provider_affiliation', schema='oneview', type_='foreignkey')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key('fk_provider_affiliation_provider_provider', 'provider_affiliation', 'provider', ['provider'], ['id'], source_schema='oneview', referent_schema='oneview')
    op.create_foreign_key('fk_provider_affiliation_business_business', 'provider_affiliation', 'business', ['business'], ['id'], source_schema='oneview', referent_schema='oneview')
    # ### end Alembic commands ###
