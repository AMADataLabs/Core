"""create CPT descriptions table

Revision ID: 63d7a4f55534
Revises: 
Create Date: 2020-05-01 14:16:41.488090+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '63d7a4f55534'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # op.execute('CREATE SCHEMA cpt')
    op.create_table(
        'description',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('description', sa.Unicode(200)),
        schema='cpt',
    )


def downgrade():
    op.drop_table('description')
    # op.execute('DROP SCHEMA cpt')
