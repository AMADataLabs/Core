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
        sa.Column('cpt_code', sa.String(5), primary_key=True),
        sa.Column('short', sa.String(28), nullable=False),
        sa.Column('medium', sa.String(48), nullable=False),
        sa.Column('long', sa.String(), nullable=False),
        schema='cpt',
    )
    op.create_table(
        'descriptor',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('cpt_code', sa.String(5), sa.ForeignKey("cpt.description.cpt_code"), nullable=False),
        sa.Column('concept_id', sa.String(5), nullable=False),
        sa.Column('clinician', sa.String, nullable=False),
        sa.Column('consumer', sa.String, nullable=False),
        schema='cpt',
    )


def downgrade():
    op.drop_table('descriptor', schema='cpt')
    op.drop_table('description', schema='cpt')
    # op.execute('DROP SCHEMA cpt')
