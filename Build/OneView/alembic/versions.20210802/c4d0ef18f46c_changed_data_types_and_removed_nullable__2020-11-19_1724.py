"""Changed data types and removed nullable constraint for residency

Revision ID: c4d0ef18f46c
Revises: 9e4b7596991c
Create Date: 2020-11-19 17:24:21.432904+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c4d0ef18f46c'
down_revision = '9e4b7596991c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('fk_credentialing_customer_institution_residency_program_1049', 'credentialing_customer_institution',
                       schema='oneview', type_='foreignkey')
    op.drop_constraint('fk_residency_program_institution_residency_program_institution', 'residency_program', schema='oneview', type_='foreignkey')
    op.drop_constraint('fk_residency_program_personnel_member_program_residency_program', 'residency_program_personnel_member',
                       schema='oneview', type_='foreignkey')
    op.drop_constraint('fk_residency_program_physician_personnel_member_residen_8bbc',
                       'residency_program_physician',
                       schema='oneview', type_='foreignkey')
    op.alter_column('residency_program_physician', 'personnel_member',
                    existing_type=sa.INTEGER(),
                    type_=sa.String(),
                    existing_nullable=False,
                    schema='oneview')
    op.alter_column('credentialing_customer_institution', 'residency_program_institution',
                    existing_type=sa.INTEGER(),
                    type_=sa.String(),
                    existing_nullable=False,
                    schema='oneview')
    op.alter_column('residency_program_personnel_member', 'program',
                    existing_type=sa.INTEGER(),
                    type_=sa.String(),
                    existing_nullable=False,
                    schema='oneview')
    op.alter_column('residency_program', 'address_1',
               existing_type=sa.VARCHAR(),
               nullable=True,
               schema='oneview')
    op.alter_column('residency_program', 'address_2',
               existing_type=sa.VARCHAR(),
               nullable=True,
               schema='oneview')
    op.alter_column('residency_program', 'address_3',
               existing_type=sa.VARCHAR(),
               nullable=True,
               schema='oneview')
    op.alter_column('residency_program', 'address_type',
               existing_type=sa.VARCHAR(),
               nullable=True,
               schema='oneview')
    op.alter_column('residency_program', 'city',
               existing_type=sa.VARCHAR(),
               nullable=True,
               schema='oneview')
    op.alter_column('residency_program', 'id',
               existing_type=sa.INTEGER(),
               type_=sa.String(),
               existing_server_default=sa.text("nextval('oneview.residency_program_id_seq'::regclass)"),
               schema='oneview')
    op.alter_column('residency_program', 'institution',
               existing_type=sa.INTEGER(),
               type_=sa.String(),
               nullable=True,
               schema='oneview')
    op.alter_column('residency_program', 'name',
               existing_type=sa.VARCHAR(),
               nullable=True,
               schema='oneview')
    op.alter_column('residency_program', 'old_name',
               existing_type=sa.VARCHAR(),
               nullable=True,
               schema='oneview')
    op.alter_column('residency_program', 'state',
               existing_type=sa.VARCHAR(),
               nullable=True,
               schema='oneview')
    op.alter_column('residency_program', 'web_address',
               existing_type=sa.VARCHAR(),
               nullable=True,
               schema='oneview')
    op.alter_column('residency_program', 'zipcode',
               existing_type=sa.VARCHAR(),
               nullable=True,
               schema='oneview')
    op.alter_column('residency_program_institution', 'id',
               existing_type=sa.INTEGER(),
               type_=sa.String(),
               existing_server_default=sa.text("nextval('oneview.residency_program_institution_id_seq'::regclass)"),
               schema='oneview')
    op.alter_column('residency_program_personnel_member', 'aamc_id',
               existing_type=sa.INTEGER(),
               type_=sa.String(),
               nullable=True,
               schema='oneview')
    op.alter_column('residency_program_personnel_member', 'degree_1',
               existing_type=sa.VARCHAR(),
               nullable=True,
               schema='oneview')
    op.alter_column('residency_program_personnel_member', 'degree_2',
               existing_type=sa.VARCHAR(),
               nullable=True,
               schema='oneview')
    op.alter_column('residency_program_personnel_member', 'degree_3',
               existing_type=sa.VARCHAR(),
               nullable=True,
               schema='oneview')
    op.alter_column('residency_program_personnel_member', 'email',
               existing_type=sa.VARCHAR(),
               nullable=True,
               schema='oneview')
    op.alter_column('residency_program_personnel_member', 'first_name',
               existing_type=sa.VARCHAR(),
               nullable=True,
               schema='oneview')
    op.alter_column('residency_program_personnel_member', 'id',
               existing_type=sa.INTEGER(),
               type_=sa.String(),
               existing_server_default=sa.text("nextval('oneview.residency_program_personnel_member_id_seq'::regclass)"),
               schema='oneview')
    op.alter_column('residency_program_personnel_member', 'last_name',
               existing_type=sa.VARCHAR(),
               nullable=True,
               schema='oneview')
    op.alter_column('residency_program_personnel_member', 'middle_name',
               existing_type=sa.VARCHAR(),
               nullable=True,
               schema='oneview')
    op.alter_column('residency_program_personnel_member', 'personnel_type',
               existing_type=sa.VARCHAR(),
               nullable=True,
               schema='oneview')
    op.alter_column('residency_program_personnel_member', 'phone_number',
               existing_type=sa.VARCHAR(),
               nullable=True,
               schema='oneview')
    op.alter_column('residency_program_personnel_member', 'suffix_name',
               existing_type=sa.VARCHAR(),
               nullable=True,
               schema='oneview')
    op.drop_constraint('uq_residency_program_personnel_member_aamc_id', 'residency_program_personnel_member', schema='oneview', type_='unique')
    op.create_foreign_key('fk_residency_program_personnel_member_program_residency_program', 'residency_program_personnel_member',
                          'residency_program', ['program'], ['id'], source_schema='oneview',
                          referent_schema='oneview')
    op.create_foreign_key('fk_credentialing_customer_institution_residency_program_1049',
                          'credentialing_customer_institution',
                          'residency_program_institution', ['residency_program_institution'], ['id'], source_schema='oneview',
                          referent_schema='oneview')
    op.create_foreign_key('fk_residency_program_physician_personnel_member_residen_8bbc',
                          'residency_program_physician',
                          'residency_program_personnel_member', ['personnel_member'], ['id'],
                          source_schema='oneview',
                          referent_schema='oneview')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('uq_residency_program_personnel_member_aamc_id', 'residency_program_personnel_member', ['aamc_id'], schema='oneview')
    op.alter_column('residency_program_personnel_member', 'suffix_name',
               existing_type=sa.VARCHAR(),
               nullable=False,
               schema='oneview')
    op.alter_column('residency_program_personnel_member', 'program',
               existing_type=sa.String(),
               type_=sa.INTEGER(),
               existing_nullable=False,
               schema='oneview')
    op.alter_column('residency_program_physician', 'personnel_member',
                    existing_type=sa.String(),
                    type_=sa.INTEGER(),
                    existing_nullable=False,
                    schema='oneview')
    op.alter_column('residency_program_personnel_member', 'phone_number',
               existing_type=sa.VARCHAR(),
               nullable=False,
               schema='oneview')
    op.alter_column('residency_program_personnel_member', 'personnel_type',
               existing_type=sa.VARCHAR(),
               nullable=False,
               schema='oneview')
    op.alter_column('residency_program_personnel_member', 'middle_name',
               existing_type=sa.VARCHAR(),
               nullable=False,
               schema='oneview')
    op.alter_column('residency_program_personnel_member', 'last_name',
               existing_type=sa.VARCHAR(),
               nullable=False,
               schema='oneview')
    op.alter_column('residency_program_personnel_member', 'id',
               existing_type=sa.String(),
               type_=sa.INTEGER(),
               existing_server_default=sa.text("nextval('oneview.residency_program_personnel_member_id_seq'::regclass)"),
               schema='oneview')
    op.alter_column('residency_program_personnel_member', 'first_name',
               existing_type=sa.VARCHAR(),
               nullable=False,
               schema='oneview')
    op.alter_column('residency_program_personnel_member', 'email',
               existing_type=sa.VARCHAR(),
               nullable=False,
               schema='oneview')
    op.alter_column('residency_program_personnel_member', 'degree_3',
               existing_type=sa.VARCHAR(),
               nullable=False,
               schema='oneview')
    op.alter_column('residency_program_personnel_member', 'degree_2',
               existing_type=sa.VARCHAR(),
               nullable=False,
               schema='oneview')
    op.alter_column('residency_program_personnel_member', 'degree_1',
               existing_type=sa.VARCHAR(),
               nullable=False,
               schema='oneview')
    op.alter_column('residency_program_personnel_member', 'aamc_id',
               existing_type=sa.String(),
               type_=sa.INTEGER(),
               nullable=False,
               schema='oneview')
    op.alter_column('residency_program_institution', 'id',
               existing_type=sa.String(),
               type_=sa.INTEGER(),
               existing_server_default=sa.text("nextval('oneview.residency_program_institution_id_seq'::regclass)"),
               schema='oneview')
    op.create_foreign_key('fk_residency_program_institution_residency_program_institution', 'residency_program', 'residency_program_institution', ['institution'], ['id'], source_schema='oneview', referent_schema='oneview')
    op.alter_column('residency_program', 'zipcode',
               existing_type=sa.VARCHAR(),
               nullable=False,
               schema='oneview')
    op.alter_column('residency_program', 'web_address',
               existing_type=sa.VARCHAR(),
               nullable=False,
               schema='oneview')
    op.alter_column('residency_program', 'state',
               existing_type=sa.VARCHAR(),
               nullable=False,
               schema='oneview')
    op.alter_column('residency_program', 'old_name',
               existing_type=sa.VARCHAR(),
               nullable=False,
               schema='oneview')
    op.alter_column('residency_program', 'name',
               existing_type=sa.VARCHAR(),
               nullable=False,
               schema='oneview')
    op.alter_column('residency_program', 'institution',
               existing_type=sa.String(),
               type_=sa.INTEGER(),
               nullable=False,
               schema='oneview')
    op.alter_column('residency_program', 'id',
               existing_type=sa.String(),
               type_=sa.INTEGER(),
               existing_server_default=sa.text("nextval('oneview.residency_program_id_seq'::regclass)"),
               schema='oneview')
    op.alter_column('residency_program', 'city',
               existing_type=sa.VARCHAR(),
               nullable=False,
               schema='oneview')
    op.alter_column('residency_program', 'address_type',
               existing_type=sa.VARCHAR(),
               nullable=False,
               schema='oneview')
    op.alter_column('residency_program', 'address_3',
               existing_type=sa.VARCHAR(),
               nullable=False,
               schema='oneview')
    op.alter_column('residency_program', 'address_2',
               existing_type=sa.VARCHAR(),
               nullable=False,
               schema='oneview')
    op.alter_column('residency_program', 'address_1',
               existing_type=sa.VARCHAR(),
               nullable=False,
               schema='oneview')
    op.alter_column('credentialing_customer_institution', 'residency_program_institution',
                    existing_type=sa.VARCHAR(),
                    type_=sa.String(),
                    existing_nullable=False,
                    schema='oneview')
    # ### end Alembic commands ###
