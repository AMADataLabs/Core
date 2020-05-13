"""Add dates column

Revision ID: 3d85a55f9934
Revises: 376b3d1b223c
Create Date: 2020-05-13 20:05:02.997193+00:00

"""
from alembic import op
from sqlalchemy import Column, String

# revision identifiers, used by Alembic.
revision = '3d85a55f9934'
down_revision = '376b3d1b223c'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('Descriptions',
                  Column('date_created', String()), schema='cpt'
                  )
    op.add_column('Descriptions',
                  Column('date_modified', String()), schema='cpt'
                  )
    op.add_column('Descriptions',
                  Column('date_created', String()), schema='cpt'
                  )
    op.add_column('Descriptor',
                  Column('date_created', String()), schema='cpt'
                  )
    op.add_column('Descriptor',
                  Column('date_modified', String()), schema='cpt'
                  )
    op.add_column('Modifier',
                  Column('date_modified', String()), schema='cpt'
                  )
    op.add_column('Modifier',
                  Column('date_modified', String()), schema='cpt'
                  )


def downgrade():
    pass
