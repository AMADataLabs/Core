"""Initial release schedule. Mod dates. Delete flags.

Revision ID: c52511ce9623
Revises: 45442f00f60f
Create Date: 2020-06-16 20:41:20.986583+00:00

"""
from alembic import op
import sqlalchemy as sa

import datalabs.etl.cpt.dbmodel as model


# revision identifiers, used by Alembic.
revision = 'c52511ce9623'
down_revision = '45442f00f60f'
branch_labels = None
depends_on = None

TABLE_NAMES = [
    'clinician_descriptor',
    'code',
    'short_descriptor',
    'medium_descriptor',
    'long_descriptor',
    'concept',
    'consumer_descriptor',
    'lab',
    'manufacturer',
    'modifier',
    'pla_code',
    'pla_short_descriptor',
    'pla_medium_descriptor',
    'pla_long_descriptor',
]


def upgrade():
    _upgrade_tables()

    _upgrade_data()

    _constrain_tables()


def downgrade():
    _downgrade_data()

    _downgrade_tables()


def _upgrade_tables():
    _add_columns()

    op.alter_column('release', 'type',
               existing_type=sa.VARCHAR(length=3),
               type_=sa.String(length=6),
               existing_nullable=False,
               schema='cpt')

    op.add_column('release_type', sa.Column('effective_day', sa.Integer(), nullable=False), schema='cpt')
    op.add_column('release_type', sa.Column('effective_month', sa.String(length=3), nullable=False), schema='cpt')
    op.add_column('release_type', sa.Column('publish_day', sa.Integer(), nullable=False), schema='cpt')
    op.add_column('release_type', sa.Column('publish_month', sa.String(length=3), nullable=False), schema='cpt')
    op.alter_column('release_type', 'type',
               existing_type=sa.VARCHAR(length=3),
               type_=sa.String(length=6),
               schema='cpt')


def _upgrade_data():
    _initialize_columns()

    _add_release_types()


def _constrain_tables():
    _constrain_deleted_columns()

    _constrain_modified_columns()


def _add_columns():
    for table_name in TABLE_NAMES:
        op.add_column(table_name, sa.Column('deleted', sa.Boolean(), nullable=True), schema='cpt')
        op.add_column(table_name, sa.Column('modified_date', sa.Date(), nullable=True), schema='cpt')


def _initialize_columns():
    for table_name in TABLE_NAMES:
        op.execute(f"update cpt.{table_name} set deleted='false'")
        op.execute(f"update cpt.{table_name} set modified_date='20200131'")


def _add_release_types():
    release_types = model.ReleaseType.__table__

    op.bulk_insert(release_types,
        [
            {
                'type': 'ANNUAL',
                'publish_month': 'Sep',
                'publish_day': 1,
                'effective_month': 'Jan',
                'effective_day': 1
            },
            {
                'type': 'PLA-Q1',
                'publish_month': 'Jan',
                'publish_day': 1,
                'effective_month': 'Apr',
                'effective_day': 1
            },
            {
                'type': 'PLA-Q2',
                'publish_month': 'Apr',
                'publish_day': 1,
                'effective_month': 'Jul',
                'effective_day': 1
            },
            {
                'type': 'PLA-Q3',
                'publish_month': 'Jul',
                'publish_day': 1,
                'effective_month': 'Oct',
                'effective_day': 1
            },
            {
                'type': 'PLA-Q4',
                'publish_month': 'Oct',
                'publish_day': 1,
                'effective_month': 'Jan',
                'effective_day': 1
            },
            {
                'type': 'OTHER',
                'publish_month': 'N/A',
                'publish_day': 0,
                'effective_month': 'N/A',
                'effective_day': 0
            },
        ]
    )


def _constrain_deleted_columns():
    for table_name in TABLE_NAMES:
        op.alter_column(table_name, 'deleted', existing_nullable=True, nullable=False, schema='cpt')


def _constrain_modified_columns():
    for table_name in TABLE_NAMES:
        op.alter_column(table_name, 'modified_date', existing_nullable=True, nullable=False, schema='cpt')


def _downgrade_data():
    op.execute(f"delete from cpt.release")
    op.execute("delete from cpt.release_type")


def _downgrade_tables():
    op.alter_column('release_type', 'type',
               existing_type=sa.String(length=6),
               type_=sa.VARCHAR(length=3),
               schema='cpt')
    op.drop_column('release_type', 'publish_month', schema='cpt')
    op.drop_column('release_type', 'publish_day', schema='cpt')
    op.drop_column('release_type', 'effective_month', schema='cpt')
    op.drop_column('release_type', 'effective_day', schema='cpt')
    op.alter_column('release', 'type',
               existing_type=sa.String(length=6),
               type_=sa.VARCHAR(length=3),
               existing_nullable=False,
               schema='cpt')

    for table_name in TABLE_NAMES:
        op.drop_column(table_name, 'modified_date', schema='cpt')
        op.drop_column(table_name, 'deleted', schema='cpt')
