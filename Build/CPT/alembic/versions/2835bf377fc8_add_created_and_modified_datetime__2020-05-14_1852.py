"""Add created and modified datetime columns to descriptor tables.

Revision ID: 2835bf377fc8
Revises: fdf9036e6d91
Create Date: 2020-05-14 18:52:00.556834+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2835bf377fc8'
down_revision = 'fdf9036e6d91'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('clinician_descriptor', sa.Column('created', sa.DateTime(), nullable=False), schema='cpt')
    op.add_column('clinician_descriptor', sa.Column('modified', sa.DateTime(), nullable=False), schema='cpt')
    op.add_column('concept', sa.Column('created', sa.DateTime(), nullable=False), schema='cpt')
    op.add_column('concept', sa.Column('modified', sa.DateTime(), nullable=False), schema='cpt')
    op.add_column('consumer_descriptor', sa.Column('created', sa.DateTime(), nullable=False), schema='cpt')
    op.add_column('consumer_descriptor', sa.Column('modified', sa.DateTime(), nullable=False), schema='cpt')
    op.add_column('cpt_descriptor', sa.Column('created', sa.DateTime(), nullable=False), schema='cpt')
    op.add_column('cpt_descriptor', sa.Column('modified', sa.DateTime(), nullable=False), schema='cpt')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('cpt_descriptor', 'modified', schema='cpt')
    op.drop_column('cpt_descriptor', 'created', schema='cpt')
    op.drop_column('consumer_descriptor', 'modified', schema='cpt')
    op.drop_column('consumer_descriptor', 'created', schema='cpt')
    op.drop_column('concept', 'modified', schema='cpt')
    op.drop_column('concept', 'created', schema='cpt')
    op.drop_column('clinician_descriptor', 'modified', schema='cpt')
    op.drop_column('clinician_descriptor', 'created', schema='cpt')
    # ### end Alembic commands ###
