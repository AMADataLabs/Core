"""Update ID datatype to BitInteger.

Revision ID: edb7fe8072ab
Revises: 4283cdea4371
Create Date: 2023-03-13 20:53:17.295501+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'edb7fe8072ab'
down_revision = '4283cdea4371'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('contact', 'id',
               existing_type=sa.INTEGER(),
               type_=sa.BigInteger(),
               existing_nullable=False,
               autoincrement=True,
               existing_server_default=sa.text("nextval('marketing.contact_id_seq'::regclass)"),
               schema='marketing')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('contact', 'id',
               existing_type=sa.BigInteger(),
               type_=sa.INTEGER(),
               existing_nullable=False,
               autoincrement=True,
               existing_server_default=sa.text("nextval('marketing.contact_id_seq'::regclass)"),
               schema='marketing')
    # ### end Alembic commands ###
