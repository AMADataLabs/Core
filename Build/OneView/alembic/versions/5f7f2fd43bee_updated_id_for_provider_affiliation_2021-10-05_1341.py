"""Updated id for provider affiliation

Revision ID: 5f7f2fd43bee
Revises: eb10352ef37d
Create Date: 2021-10-05 13:41:30.943918+00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text as sql_text

# revision identifiers, used by Alembic.
revision = '5f7f2fd43bee'
down_revision = 'eb10352ef37d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('provider_affiliation', 'id',
               existing_type=sa.INTEGER(),
               type_=sa.String(),
               existing_nullable=False,
               existing_server_default=sa.text("nextval('oneview.provider_affiliation_id_seq'::regclass)"),
               schema='oneview')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('provider_affiliation', 'id',
               existing_type=sa.String(),
               type_=sa.INTEGER(),
               existing_nullable=False,
               existing_server_default=sa.text("nextval('oneview.provider_affiliation_id_seq'::regclass)"),
               schema='oneview')
    # ### end Alembic commands ###
