"""Updated iqvia data model

Revision ID: 4466ae3acc02
Revises: fba813690f36
Create Date: 2020-11-17 20:00:18.673289+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4466ae3acc02'
down_revision = 'fba813690f36'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('provider_affiliation', sa.Column('type', sa.String(), nullable=True), schema='oneview')
    op.drop_column('provider_affiliation', 'id', schema='oneview')
    op.add_column('provider_affiliation', sa.Column('id', sa.Integer(), primary_key=True, nullable=True), schema='oneview')
    # op.alter_column('provider_affiliation', 'id',
    #            existing_type=sa.VARCHAR(),
    #            type_=sa.Integer(),
    #            autoincrement=True,
    #            existing_server_default=sa.text("nextval('oneview.provider_affiliation_id_seq'::regclass)"),
    #            schema='oneview')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # op.alter_column('provider_affiliation', 'id',
    #            existing_type=sa.Integer(),
    #            type_=sa.VARCHAR(),
    #            autoincrement=True,
    #            existing_server_default=sa.text("nextval('oneview.provider_affiliation_id_seq'::regclass)"),
    #            schema='oneview')
    op.drop_column('provider_affiliation', 'type', schema='oneview')
    op.drop_column('provider_affiliation', 'id', schema='oneview')
    op.add_column('provider_affiliation', sa.Column('id', sa.String(), nullable=True, primary_key=True), schema='oneview')
    # ### end Alembic commands ###
