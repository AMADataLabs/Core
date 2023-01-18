"""Update data model

Revision ID: 256ef8f273b2
Revises: 9cfb55308ed2
Create Date: 2021-05-25 16:44:00.405298+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '256ef8f273b2'
down_revision = '9cfb55308ed2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('core_based_statistical_area_melissa',
    sa.Column('code', sa.String(), nullable=False),
    sa.Column('type', sa.String(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('level', sa.String(), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('code', name=op.f('pk_core_based_statistical_area_melissa')),
    schema='oneview'
    )
    op.drop_constraint('fk_zip_code_core_based_statistical_areas_core_based_sta_d53e',
                       'zip_code_core_based_statistical_areas', schema='oneview', type_='foreignkey')
    op.drop_table('core_based_statistical_area_zip_code', schema='oneview')
    op.add_column('census', sa.Column('hawaiian', sa.Integer(), nullable=False), schema='oneview')
    op.drop_column('census', 'hawaian', schema='oneview')
    op.add_column('credentialing_customer_business', sa.Column('id', sa.Integer(), nullable=False), schema='oneview')
    # op.create_foreign_key(op.f('fk_credentialing_customer_business_customer_credentialing_customer'), 'credentialing_customer_business', 'credentialing_customer', ['customer'], ['id'], source_schema='oneview', referent_schema='oneview')
    op.add_column('credentialing_customer_institution', sa.Column('id', sa.Integer(), nullable=False), schema='oneview')
    # op.create_foreign_key(op.f('fk_credentialing_customer_institution_customer_credentialing_customer'), 'credentialing_customer_institution', 'credentialing_customer', ['customer'], ['id'], source_schema='oneview', referent_schema='oneview')
    op.add_column('credentialing_order', sa.Column('quantity', sa.String(), nullable=False), schema='oneview')
    # op.create_foreign_key(op.f('fk_credentialing_order_customer_credentialing_customer'), 'credentialing_order', 'credentialing_customer', ['customer'], ['id'], source_schema='oneview', referent_schema='oneview')
    op.drop_column('credentialing_order', 'person_id', schema='oneview')
    op.add_column('physician', sa.Column('national_provider_identifier', sa.String(), nullable=True), schema='oneview')
    op.add_column('physician', sa.Column('type', sa.String(), nullable=False), schema='oneview')
    op.drop_column('physician', 'physician_type', schema='oneview')
    op.add_column('provider', sa.Column('unique_physician_identification_number', sa.String(), nullable=True), schema='oneview')
    op.drop_column('provider', 'universal_provider_identification', schema='oneview')
    op.add_column('residency_program', sa.Column('american_osteopathic_association_indicator_program', sa.String(), nullable=True), schema='oneview')
    op.drop_column('residency_program', 'american_osteopathic_association_indicator_program_id', schema='oneview')
    op.add_column('residency_program_institution', sa.Column('affiliation', sa.String(), nullable=True), schema='oneview')
    op.add_column('residency_program_institution', sa.Column('name', sa.String(), nullable=True), schema='oneview')
    op.drop_column('residency_program_institution', 'program', schema='oneview')
    op.drop_column('residency_program_institution', 'sponsors_residents', schema='oneview')
    op.add_column('residency_program_physician', sa.Column('id', sa.Integer(), nullable=False), schema='oneview')
    op.create_foreign_key(op.f('fk_zip_code_core_based_statistical_areas_core_based_statistical_area_core_based_statistical_area_melissa'), 'zip_code_core_based_statistical_areas', 'core_based_statistical_area_melissa', ['core_based_statistical_area'], ['code'], source_schema='oneview', referent_schema='oneview')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(op.f('fk_zip_code_core_based_statistical_areas_core_based_statistical_area_core_based_statistical_area_melissa'), 'zip_code_core_based_statistical_areas', schema='oneview', type_='foreignkey')
    op.create_foreign_key('fk_zip_code_core_based_statistical_areas_core_based_sta_d53e', 'zip_code_core_based_statistical_areas', 'core_based_statistical_area_zip_code', ['core_based_statistical_area'], ['code'], source_schema='oneview', referent_schema='oneview')
    op.drop_column('residency_program_physician', 'id', schema='oneview')
    op.add_column('residency_program_institution', sa.Column('sponsors_residents', sa.BOOLEAN(), autoincrement=False, nullable=True), schema='oneview')
    op.add_column('residency_program_institution', sa.Column('program', sa.VARCHAR(), autoincrement=False, nullable=True), schema='oneview')
    op.drop_column('residency_program_institution', 'name', schema='oneview')
    op.drop_column('residency_program_institution', 'affiliation', schema='oneview')
    op.add_column('residency_program', sa.Column('american_osteopathic_association_indicator_program_id', sa.VARCHAR(), autoincrement=False, nullable=True), schema='oneview')
    op.drop_column('residency_program', 'american_osteopathic_association_indicator_program', schema='oneview')
    op.add_column('provider', sa.Column('universal_provider_identification', sa.VARCHAR(), autoincrement=False, nullable=True), schema='oneview')
    op.drop_column('provider', 'unique_physician_identification_number', schema='oneview')
    op.add_column('physician', sa.Column('physician_type', sa.VARCHAR(), autoincrement=False, nullable=False), schema='oneview')
    op.drop_column('physician', 'type', schema='oneview')
    op.drop_column('physician', 'national_provider_identifier', schema='oneview')
    op.add_column('credentialing_order', sa.Column('person_id', sa.VARCHAR(), autoincrement=False, nullable=False), schema='oneview')
    # op.drop_constraint(op.f('fk_credentialing_order_customer_credentialing_customer'), 'credentialing_order', schema='oneview', type_='foreignkey')
    op.drop_column('credentialing_order', 'quantity', schema='oneview')
    # op.drop_constraint(op.f('fk_credentialing_customer_institution_customer_credentialing_customer'), 'credentialing_customer_institution', schema='oneview', type_='foreignkey')
    op.drop_column('credentialing_customer_institution', 'id', schema='oneview')
    # op.drop_constraint(op.f('fk_credentialing_customer_business_customer_credentialing_customer'), 'credentialing_customer_business', schema='oneview', type_='foreignkey')
    op.drop_column('credentialing_customer_business', 'id', schema='oneview')
    op.add_column('census', sa.Column('hawaian', sa.INTEGER(), autoincrement=False, nullable=False), schema='oneview')
    op.drop_column('census', 'hawaiian', schema='oneview')
    op.create_table('core_based_statistical_area_zip_code',
    sa.Column('code', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('type', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('title', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('level', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('status', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('code', name='pk_core_based_statistical_area_zip_code'),
    schema='oneview'
    )
    op.drop_table('core_based_statistical_area_melissa', schema='oneview')
    # ### end Alembic commands ###