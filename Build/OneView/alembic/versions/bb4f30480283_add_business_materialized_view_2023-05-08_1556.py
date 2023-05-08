"""add business materialized view

Revision ID: bb4f30480283
Revises: 2893c7b0bb27
Create Date: 2023-05-08 15:56:59.306491+00:00

"""
from alembic import op
import sqlalchemy as sa
from alembic_utils.pg_materialized_view import PGMaterializedView
from sqlalchemy import text as sql_text
from alembic_utils.pg_trigger import PGTrigger
from sqlalchemy import text as sql_text
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'bb4f30480283'
down_revision = '2893c7b0bb27'
branch_labels = None
depends_on = None


def upgrade():
    oneview_business_view = PGMaterializedView(
                schema="oneview",
                signature="business_view",
                definition='SELECT business.id,\n    business.name,\n    business.doing_business_as,\n    business.iqvia_address_id,\n    business.physical_address_1,\n    business.physical_address_2,\n    business.physical_city,\n    business.physical_state,\n    substr((business.physical_zipcode)::text, 1, 5) AS physical_zipcode5,\n    business.postal_address_1,\n    business.postal_address_2,\n    business.postal_city,\n    business.postal_state,\n    business.postal_zipcode,\n    business.phone,\n    business.fax,\n    business.website,\n    business.latitude,\n    business.longitude,\n    business.owner_status,\n    business.profit_status,\n    business.primary_class_of_trade,\n    business.class_of_trade_classification,\n    business.class_of_trade_classification_description,\n    business.class_of_trade_facility_type,\n    business.class_of_trade_facility_type_description,\n    business.class_of_trade_specialty,\n    business.class_of_trade_specialty_description,\n    business.record_type,\n    business.total_licensed_beds,\n    business.total_census_beds,\n    business.total_staffed_beds,\n    business.teaching_hospital,\n    business.hospital_care,\n    business.metropolitan_statistical_area,\n    business.federal_information_processing_standard_state,\n    business.federal_information_processing_standard_county,\n    business.number_of_providers,\n    business.electronic_medical_record,\n    business.electronically_prescribe,\n    business.pay_for_performance,\n    business.deactivation_reason,\n    business.replacement_business,\n    business.status_indicator\n   FROM oneview.business',
                with_data=True
            )

    op.create_entity(oneview_business_view)

    op.create_index('physical_zipcode5_index', 'business_view', ['physical_zipcode5'], schema='oneview')


def downgrade():
    oneview_business_view = PGMaterializedView(
                schema="oneview",
                signature="business_view",
                definition='SELECT business.id,\n    business.name,\n    business.doing_business_as,\n    business.iqvia_address_id,\n    business.physical_address_1,\n    business.physical_address_2,\n    business.physical_city,\n    business.physical_state,\n    substr((business.physical_zipcode)::text, 1, 5) AS physical_zipcode5,\n    business.postal_address_1,\n    business.postal_address_2,\n    business.postal_city,\n    business.postal_state,\n    business.postal_zipcode,\n    business.phone,\n    business.fax,\n    business.website,\n    business.latitude,\n    business.longitude,\n    business.owner_status,\n    business.profit_status,\n    business.primary_class_of_trade,\n    business.class_of_trade_classification,\n    business.class_of_trade_classification_description,\n    business.class_of_trade_facility_type,\n    business.class_of_trade_facility_type_description,\n    business.class_of_trade_specialty,\n    business.class_of_trade_specialty_description,\n    business.record_type,\n    business.total_licensed_beds,\n    business.total_census_beds,\n    business.total_staffed_beds,\n    business.teaching_hospital,\n    business.hospital_care,\n    business.metropolitan_statistical_area,\n    business.federal_information_processing_standard_state,\n    business.federal_information_processing_standard_county,\n    business.number_of_providers,\n    business.electronic_medical_record,\n    business.electronically_prescribe,\n    business.pay_for_performance,\n    business.deactivation_reason,\n    business.replacement_business,\n    business.status_indicator\n   FROM oneview.business',
                with_data=True
            )

    op.drop_entity(oneview_business_view)

    op.drop_index('physical_zipcode5_index', 'business_view', schema='oneview')
