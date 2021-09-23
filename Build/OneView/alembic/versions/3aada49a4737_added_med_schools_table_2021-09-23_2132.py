"""Added med schools table

Revision ID: 3aada49a4737
Revises: 05392903ddd6
Create Date: 2021-09-23 21:32:36.655619+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3aada49a4737'
down_revision = '05392903ddd6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('medical_school',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_medical_school')),
    schema='oneview'
    )
    op.drop_table('association_status', schema='oneview')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('association_status',
    sa.Column('id', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('description', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='pk_association_status'),
    schema='oneview'
    )
    op.drop_table('medical_school', schema='oneview')
    # ### end Alembic commands ###
