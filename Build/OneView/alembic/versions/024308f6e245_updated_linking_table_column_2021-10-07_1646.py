"""Updated linking table column

Revision ID: 024308f6e245
Revises: eb88a3ad7449
Create Date: 2021-10-07 16:46:03.513584+00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text as sql_text

# revision identifiers, used by Alembic.
revision = '024308f6e245'
down_revision = 'eb88a3ad7449'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('residency_program_physician', sa.Column('program', sa.String(), nullable=False), schema='oneview')
    op.drop_constraint('uq_residency_program_physician_personnel_member', 'residency_program_physician', schema='oneview', type_='unique')
    op.create_unique_constraint(op.f('uq_residency_program_physician_program'), 'residency_program_physician', ['program'], schema='oneview')
    op.drop_constraint('fk_residency_program_physician_personnel_member_residen_8bbc', 'residency_program_physician', schema='oneview', type_='foreignkey')
    op.create_foreign_key(op.f('fk_residency_program_physician_program_residency_program'), 'residency_program_physician', 'residency_program', ['program'], ['id'], source_schema='oneview', referent_schema='oneview')
    op.drop_column('residency_program_physician', 'personnel_member', schema='oneview')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('residency_program_physician', sa.Column('personnel_member', sa.VARCHAR(), autoincrement=False, nullable=False), schema='oneview')
    op.drop_constraint(op.f('fk_residency_program_physician_program_residency_program'), 'residency_program_physician', schema='oneview', type_='foreignkey')
    op.create_foreign_key('fk_residency_program_physician_personnel_member_residen_8bbc', 'residency_program_physician', 'residency_program_personnel_member', ['personnel_member'], ['id'], source_schema='oneview', referent_schema='oneview')
    op.drop_constraint(op.f('uq_residency_program_physician_program'), 'residency_program_physician', schema='oneview', type_='unique')
    op.create_unique_constraint('uq_residency_program_physician_personnel_member', 'residency_program_physician', ['personnel_member'], schema='oneview')
    op.drop_column('residency_program_physician', 'program', schema='oneview')
    # ### end Alembic commands ###