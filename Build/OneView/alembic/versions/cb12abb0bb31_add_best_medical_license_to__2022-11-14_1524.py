"""add best medical license to materialized views

Revision ID: cb12abb0bb31
Revises: aff01331a7fa
Create Date: 2022-11-14 15:24:05.325523+00:00

"""
from alembic import op
import sqlalchemy as sa
from alembic_utils.pg_materialized_view import PGMaterializedView
from sqlalchemy import text as sql_text
from alembic_utils.pg_trigger import PGTrigger
from sqlalchemy import text as sql_text
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'cb12abb0bb31'
down_revision = 'aff01331a7fa'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    oneview_mat_phy_view = PGMaterializedView(
                schema="oneview",
                signature="mat_phy_view",
                definition='SELECT phy.medical_education_number AS phy_medical_education_number,\n    phy.address_type AS phy_address_type,\n    phy.mailing_name AS phy_mailing_name,\n    phy.last_name AS phy_last_name,\n    phy.first_name AS phy_first_name,\n    phy.middle_name AS phy_middle_name,\n    phy.name_suffix AS phy_name_suffix,\n    phy.preferred_address_2 AS phy_preferred_address_2,\n    phy.preferred_address_1 AS phy_preferred_address_1,\n    phy.city AS phy_city,\n    phy.state AS phy_state,\n    phy.zipcode AS phy_zipcode,\n    phy.sector AS phy_sector,\n    phy.carrier_route AS phy_carrier_route,\n    phy.address_undeliverable AS phy_address_undeliverable,\n    phy.federal_information_processing_standard_county AS phy_federal_information_processing_standard_county,\n    phy.federal_information_processing_standard_state AS phy_federal_information_processing_standard_state,\n    phy.printer_control_code_begin AS phy_printer_control_code_begin,\n    phy.barcode_zipcode AS phy_barcode_zipcode,\n    phy.barcode_zipcode_plus_4 AS phy_barcode_zipcode_plus_4,\n    phy.delivery_point AS phy_delivery_point,\n    phy.check_digit AS phy_check_digit,\n    phy.printer_control_code_end AS phy_printer_control_code_end,\n    phy.census_region AS phy_region,\n    phy.census_division AS phy_division,\n    phy.census_group AS phy_group,\n    phy.census_tract AS phy_tract,\n    phy.census_suffix AS phy_suffix,\n    phy.census_block_group AS phy_block_group,\n    phy.metropolitan_statistical_area_population AS phy_metropolitan_statistical_area_population,\n    phy.micro_metro_indicator AS phy_micro_metro_indicator,\n    phy.core_based_statistical_area AS phy_core_based_statistical_area_id,\n    cbsa.description AS phy_core_based_statistical_area,\n    phy.core_based_statistical_area_division AS phy_core_based_statistical_area_division,\n    phy.degree_type AS phy_degree_type,\n    phy.birth_year AS phy_birth_year,\n    phy.birth_city AS phy_birth_city,\n    phy.birth_state AS phy_birth_state,\n    phy.birth_country AS phy_birth_country,\n    phy.gender AS phy_gender,\n    phy.telephone_number AS phy_telephone_number,\n    phy.presumed_dead AS phy_presumed_dead,\n    phy.fax_number AS phy_fax_number,\n    phy.type_of_practice AS phy_type_of_practice,\n    top.description AS phy_type_of_practice_description,\n    phy.present_employment AS phy_present_employment_id,\n    pe.description AS phy_present_employment,\n    phy.primary_specialty AS phy_primary_specialty_id,\n    spe.description AS phy_primary_specialty,\n    phy.secondary_specialty AS phy_secondary_specialty,\n    phy.major_professional_activity AS phy_mpa_id,\n    mpa.description AS phy_major_professional_activity,\n    phy.physician_recognition_award_recipient AS phy_physician_recognition_award_recipient,\n    phy.physician_recognition_award_expiration_date AS phy_physician_recognition_award_expiration_date,\n    phy.graduate_medical_education_confirm AS phy_graduate_medical_education_confirm,\n    phy.from_date AS phy_from_date,\n    phy.end_date AS phy_end_date,\n    phy.year_in_program AS phy_year_in_program,\n    phy.post_graduate_year AS phy_post_graduate_year,\n    phy.graduate_medical_education_primary_specialty AS phy_graduate_medical_education_primary_specialty,\n    phy.graduate_medical_education_secondary_specialty AS phy_graduate_medical_education_secondary_specialty,\n    phy.training_type AS phy_training_type,\n    phy.graduate_medical_education_hospital_state AS phy_graduate_medical_education_hospital_state,\n    phy.graduate_medical_education_hospital AS phy_graduate_medical_education_hospital,\n    phy.medical_school_state AS phy_medical_school_state,\n    substr(phy.medical_school_state::text, 1, 1) AS phy_medical_school_indicator,\n    phy.medical_school AS phy_medical_school,\n    ms.description AS phy_medical_school_name,\n    phy.medical_school_graduation_year AS phy_medical_school_graduation_year,\n    phy.no_contact_type AS phy_no_contact_type,\n    phy.no_web AS phy_no_web,\n    phy.physician_data_restriction_program AS phy_physician_data_restriction_program,\n    phy.physician_data_restriction_program_date AS phy_physician_data_restriction_program_date,\n    phy.polo_address_2 AS phy_polo_address_2,\n    phy.polo_address_1 AS phy_polo_address_1,\n    phy.polo_city AS phy_polo_city,\n    phy.polo_state AS phy_polo_state,\n    phy.polo_zipcode AS phy_polo_zipcode,\n    phy.polo_sector AS phy_polo_sector,\n    phy.polo_carrier_route AS phy_polo_carrier_route,\n    phy.most_recent_former_last_name AS phy_most_recent_former_last_name,\n    phy.most_recent_former_middle_name AS phy_most_recent_former_middle_name,\n    phy.most_recent_former_first_name AS phy_most_recent_former_first_name,\n    phy.next_most_recent_former_last_name AS phy_next_most_recent_former_last_name,\n    phy.next_most_recent_former_middle_name AS phy_next_most_recent_former_middle_name,\n    phy.next_most_recent_former_first_name AS phy_next_most_recent_former_first_name,\n    phy.national_provider_identifier AS phy_national_provider_identifier,\n    phy.party_id AS phy_party_id,\n    phy.entity_id AS phy_entity_id,\n    phy.type AS phy_type,\n    phy.no_release AS phy_no_release,\n    phy.membership_status AS phy_membership_status,\n    phy.has_email AS phy_has_email,\n    bu.name AS aff_business_name,\n    bu.owner_status AS aff_owner_status,\n    bu.profit_status AS aff_profit_status,\n    bu.status_indicator AS aff_status_indicator,\n    bu.electronically_prescribe AS aff_electronically_prescribe,\n    bu.number_of_providers AS aff_physicians_affiliated,\n    bu.class_of_trade_classification_description AS aff_organization_classification,\n    bu.class_of_trade_facility_type_description AS aff_organization_type,\n    bu.class_of_trade_specialty_description AS aff_organization_specialty,\n    bu.physical_state AS aff_physical_state,\n    bu.federal_information_processing_standard_county AS aff_federal_information_processing_standard_county,\n    bu.physical_city AS aff_physical_city,\n    bu.metropolitan_statistical_area AS aff_msa,\n    bu.physical_zipcode AS aff_physical_zipcode,\n    substr(bu.physical_zipcode::text, 1, 5) AS aff_physician_zipcode_5digits,\n    bu.teaching_hospital AS aff_teaching_hospital,\n    pa.type AS aff_type,\n    pa.description AS aff_hospital_affiliation,\n    pa.group_description AS aff_group_affiliation,\n    pa."primary" AS aff_affiliation_status,\n    rpp.id AS phy_residency_id,\n    zc.metropolitan_statistical_area AS phy_metropolitan_statistical_area,\n    zc.primary_metropolitan_statistical_area AS phy_primary_metropolitan_statistical_area,\n    zc.county_federal_information_processing AS phy_zipcode_county_federal_information_processing,\n    zc.state AS phy_zipcode_state,\n    msa.name AS phy_metropolitan_statistical_area_description,\n    msa.code AS phy_msa_code,\n    msa.type AS phy_msa_type,\n    msa.consolidated_metropolitan_statistical_area,\n    pa.best as aff_affiliation_best_status,\n    ml.state as phy_license_state\nFROM oneview.physician phy\n    LEFT JOIN oneview.type_of_practice top ON phy.type_of_practice::text = top.id::text\n    LEFT JOIN oneview.present_employment pe ON phy.present_employment::text = pe.id::text\n    LEFT JOIN oneview.major_professional_activity mpa ON phy.major_professional_activity::text = mpa.id::text\n    LEFT JOIN oneview.provider_affiliation pa ON phy.medical_education_number::text = pa.medical_education_number::text\n    LEFT JOIN oneview.business bu ON pa.business::text = bu.id::text\n    LEFT JOIN oneview.specialty spe ON phy.primary_specialty::text = spe.id::text\n    LEFT JOIN oneview.core_based_statistical_area cbsa ON phy.core_based_statistical_area::text = cbsa.id::text\n    LEFT JOIN oneview.residency_program_physician rpp ON phy.medical_education_number::text = rpp.medical_education_number::text\n    LEFT JOIN oneview.zip_code zc ON phy.zipcode::text = zc.zip_code::text\n    LEFT JOIN oneview.metropolitan_statistical_area msa ON msa.code::text = zc.metropolitan_statistical_area::text\n    LEFT JOIN oneview.medical_school ms ON substr(ms.id::text, 1, 3) = phy.medical_school_state::text AND substr(ms.id::text, 4, 5) = phy.medical_school::text\n    LEFT JOIN oneview.medical_license ml ON phy.medical_education_number::text = ml.medical_education_number::text\nORDER BY phy.medical_education_number',
                with_data=True
            )
    op.replace_entity(oneview_mat_phy_view)

    oneview_mat_phy_pro_view = PGMaterializedView(
                schema="oneview",
                signature="mat_phy_pro_view",
                definition='SELECT phy.medical_education_number AS phy_medical_education_number,\n    phy.address_type AS phy_address_type,\n    phy.mailing_name AS phy_mailing_name,\n    phy.last_name AS phy_last_name,\n    phy.first_name AS phy_first_name,\n    phy.middle_name AS phy_middle_name,\n    phy.name_suffix AS phy_name_suffix,\n    phy.preferred_address_2 AS phy_preferred_address_2,\n    phy.preferred_address_1 AS phy_preferred_address_1,\n    phy.city AS phy_city,\n    phy.state AS phy_state,\n    phy.zipcode AS phy_zipcode,\n    phy.sector AS phy_sector,\n    phy.carrier_route AS phy_carrier_route,\n    phy.address_undeliverable AS phy_address_undeliverable,\n    phy.federal_information_processing_standard_county AS phy_federal_information_processing_standard_county,\n    phy.federal_information_processing_standard_state AS phy_federal_information_processing_standard_state,\n    phy.printer_control_code_begin AS phy_printer_control_code_begin,\n    phy.barcode_zipcode AS phy_barcode_zipcode,\n    phy.barcode_zipcode_plus_4 AS phy_barcode_zipcode_plus_4,\n    phy.delivery_point AS phy_delivery_point,\n    phy.check_digit AS phy_check_digit,\n    phy.printer_control_code_end AS phy_printer_control_code_end,\n    phy.census_region AS phy_region,\n    phy.census_division AS phy_division,\n    phy.census_group AS phy_group,\n    phy.census_tract AS phy_tract,\n    phy.census_suffix AS phy_suffix,\n    phy.census_block_group AS phy_block_group,\n    phy.metropolitan_statistical_area_population AS phy_metropolitan_statistical_area_population,\n    phy.micro_metro_indicator AS phy_micro_metro_indicator,\n    phy.core_based_statistical_area AS phy_core_based_statistical_area_id,\n    cbsa.description AS phy_core_based_statistical_area,\n    phy.core_based_statistical_area_division AS phy_core_based_statistical_area_division,\n    phy.degree_type AS phy_degree_type,\n    phy.birth_year AS phy_birth_year,\n    phy.birth_city AS phy_birth_city,\n    phy.birth_state AS phy_birth_state,\n    phy.birth_country AS phy_birth_country,\n    phy.gender AS phy_gender,\n    phy.telephone_number AS phy_telephone_number,\n    phy.presumed_dead AS phy_presumed_dead,\n    phy.fax_number AS phy_fax_number,\n    phy.type_of_practice AS phy_type_of_practice,\n    top.description AS phy_type_of_practice_description,\n    phy.present_employment AS phy_present_employment_id,\n    pe.description AS phy_present_employment,\n    phy.primary_specialty AS phy_primary_specialty_id,\n    spe.description AS phy_primary_specialty,\n    phy.secondary_specialty AS phy_secondary_specialty,\n    phy.major_professional_activity AS phy_mpa_id,\n    mpa.description AS phy_major_professional_activity,\n    phy.physician_recognition_award_recipient AS phy_physician_recognition_award_recipient,\n    phy.physician_recognition_award_expiration_date AS phy_physician_recognition_award_expiration_date,\n    phy.graduate_medical_education_confirm AS phy_graduate_medical_education_confirm,\n    phy.from_date AS phy_from_date,\n    phy.end_date AS phy_end_date,\n    phy.year_in_program AS phy_year_in_program,\n    phy.post_graduate_year AS phy_post_graduate_year,\n    phy.graduate_medical_education_primary_specialty AS phy_graduate_medical_education_primary_specialty,\n    phy.graduate_medical_education_secondary_specialty AS phy_graduate_medical_education_secondary_specialty,\n    phy.training_type AS phy_training_type,\n    phy.graduate_medical_education_hospital_state AS phy_graduate_medical_education_hospital_state,\n    phy.graduate_medical_education_hospital AS phy_graduate_medical_education_hospital,\n    phy.medical_school_state AS phy_medical_school_state,\n    substr(phy.medical_school_state::text, 1, 1) AS phy_medical_school_indicator,\n    phy.medical_school AS phy_medical_school,\n    ms.description AS phy_medical_school_name,\n    phy.medical_school_graduation_year AS phy_medical_school_graduation_year,\n    phy.no_contact_type AS phy_no_contact_type,\n    phy.no_web AS phy_no_web,\n    phy.physician_data_restriction_program AS phy_physician_data_restriction_program,\n    phy.physician_data_restriction_program_date AS phy_physician_data_restriction_program_date,\n    phy.polo_address_2 AS phy_polo_address_2,\n    phy.polo_address_1 AS phy_polo_address_1,\n    phy.polo_city AS phy_polo_city,\n    phy.polo_state AS phy_polo_state,\n    phy.polo_zipcode AS phy_polo_zipcode,\n    phy.polo_sector AS phy_polo_sector,\n    phy.polo_carrier_route AS phy_polo_carrier_route,\n    phy.most_recent_former_last_name AS phy_most_recent_former_last_name,\n    phy.most_recent_former_middle_name AS phy_most_recent_former_middle_name,\n    phy.most_recent_former_first_name AS phy_most_recent_former_first_name,\n    phy.next_most_recent_former_last_name AS phy_next_most_recent_former_last_name,\n    phy.next_most_recent_former_middle_name AS phy_next_most_recent_former_middle_name,\n    phy.next_most_recent_former_first_name AS phy_next_most_recent_former_first_name,\n    phy.national_provider_identifier AS phy_national_provider_identifier,\n    phy.party_id AS phy_party_id,\n    phy.entity_id AS phy_entity_id,\n    phy.type AS phy_type,\n    phy.no_release AS phy_no_release,\n    phy.membership_status AS phy_membership_status,\n    phy.has_email AS phy_has_email,\n    bu.name AS aff_business_name,\n    bu.owner_status AS aff_owner_status,\n    bu.profit_status AS aff_profit_status,\n    bu.status_indicator AS aff_status_indicator,\n    bu.electronically_prescribe AS aff_electronically_prescribe,\n    bu.number_of_providers AS aff_physicians_affiliated,\n    bu.class_of_trade_classification_description AS aff_organization_classification,\n    bu.class_of_trade_facility_type_description AS aff_organization_type,\n    bu.class_of_trade_specialty_description AS aff_organization_specialty,\n    bu.physical_state AS aff_physical_state,\n    bu.federal_information_processing_standard_county AS aff_federal_information_processing_standard_county,\n    bu.physical_city AS aff_physical_city,\n    bu.metropolitan_statistical_area AS aff_msa,\n    bu.physical_zipcode AS aff_physical_zipcode,\n    substr(bu.physical_zipcode::text, 1, 5) AS aff_physician_zipcode_5digits,\n    bu.teaching_hospital AS aff_teaching_hospital,\n    pa.type AS aff_type,\n    pa.description AS aff_hospital_affiliation,\n    pa.group_description AS aff_group_affiliation,\n    pa."primary" AS aff_affiliation_status,\n    pr.first_name AS pro_first_name,\n    pr.middle_name AS pro_middle_name,\n    pr.last_name AS pro_last_name,\n    pr.primary_specialty AS pro_primary_specialty,\n    pr.suffix AS pro_suffix,\n    pr.gender AS pro_gender,\n    pr.national_provider_identifier AS pro_national_provider_identifier,\n    pr.secondary_specialty AS pro_secondary_speciality,\n    rpp.id AS phy_residency_id,\n    zc.metropolitan_statistical_area AS phy_metropolitan_statistical_area,\n    zc.primary_metropolitan_statistical_area AS phy_primary_metropolitan_statistical_area,\n    zc.county_federal_information_processing AS phy_zipcode_county_federal_information_processing,\n    zc.state AS phy_zipcode_state,\n    msa.name AS phy_metropolitan_statistical_area_description,\n    msa.code AS phy_msa_code,\n    msa.type AS phy_msa_type,\n    msa.consolidated_metropolitan_statistical_area,\n    pa.best as aff_affiliation_best_status,\n    ml.state as phy_license_state\nFROM oneview.physician phy\n    LEFT JOIN oneview.type_of_practice top ON phy.type_of_practice::text = top.id::text\n    LEFT JOIN oneview.present_employment pe ON phy.present_employment::text = pe.id::text\n    LEFT JOIN oneview.major_professional_activity mpa ON phy.major_professional_activity::text = mpa.id::text\n    LEFT JOIN oneview.provider_affiliation pa ON phy.medical_education_number::text = pa.medical_education_number::text\n    LEFT JOIN oneview.business bu ON pa.business::text = bu.id::text\n    LEFT JOIN oneview.provider pr ON phy.medical_education_number::text = pr.medical_education_number::text\n    LEFT JOIN oneview.specialty spe ON phy.primary_specialty::text = spe.id::text\n    LEFT JOIN oneview.core_based_statistical_area cbsa ON phy.core_based_statistical_area::text = cbsa.id::text\n    LEFT JOIN oneview.residency_program_physician rpp ON phy.medical_education_number::text = rpp.medical_education_number::text\n    LEFT JOIN oneview.zip_code zc ON phy.zipcode::text = zc.zip_code::text\n    LEFT JOIN oneview.metropolitan_statistical_area msa ON msa.code::text = zc.metropolitan_statistical_area::text\n    LEFT JOIN oneview.medical_school ms ON substr(ms.id::text, 1, 3) = phy.medical_school_state::text AND substr(ms.id::text, 4, 5) = phy.medical_school::text\n    LEFT JOIN oneview.medical_license ml ON phy.medical_education_number::text = ml.medical_education_number::text    \nORDER BY phy.medical_education_number',
                with_data=True
            )
    op.replace_entity(oneview_mat_phy_pro_view)

    ### Re-add Indexes ###
    op.create_index('mat_phy_aff_zipcode_index', 'mat_phy_view', ['aff_physician_zipcode_5digits'], schema='oneview')
    op.create_index('mat_phy_phy_zipcode_index', 'mat_phy_view', ['phy_zipcode'], schema='oneview')
    op.create_index('mat_phy_phy_polo_zipcode_index', 'mat_phy_view', ['phy_polo_zipcode'], schema='oneview')
    op.create_index('mat_phy_phy_type_of_practice', 'mat_phy_view', ['phy_type_of_practice'], schema='oneview')
    op.create_index('mat_phy_phy_present_employment_id', 'mat_phy_view', ['phy_present_employment_id'], schema='oneview')

    op.create_index('mat_phy_pro_aff_zipcode_index', 'mat_phy_pro_view', ['aff_physician_zipcode_5digits'], schema='oneview')
    op.create_index('mat_phy_pro_phy_zipcode_index', 'mat_phy_pro_view', ['phy_zipcode'], schema='oneview')
    op.create_index('mat_phy_pro_phy_polo_zipcode_index', 'mat_phy_pro_view', ['phy_polo_zipcode'], schema='oneview')
    op.create_index('mat_phy_pro_phy_type_of_practice', 'mat_phy_pro_view', ['phy_type_of_practice'], schema='oneview')
    op.create_index('mat_phy_pro_phy_present_employment_id', 'mat_phy_pro_view', ['phy_present_employment_id'], schema='oneview')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    oneview_mat_phy_pro_view = PGMaterializedView(
                schema="oneview",
                signature="mat_phy_pro_view",
                definition='SELECT phy.medical_education_number AS phy_medical_education_number,\n    phy.address_type AS phy_address_type,\n    phy.mailing_name AS phy_mailing_name,\n    phy.last_name AS phy_last_name,\n    phy.first_name AS phy_first_name,\n    phy.middle_name AS phy_middle_name,\n    phy.name_suffix AS phy_name_suffix,\n    phy.preferred_address_2 AS phy_preferred_address_2,\n    phy.preferred_address_1 AS phy_preferred_address_1,\n    phy.city AS phy_city,\n    phy.state AS phy_state,\n    phy.zipcode AS phy_zipcode,\n    phy.sector AS phy_sector,\n    phy.carrier_route AS phy_carrier_route,\n    phy.address_undeliverable AS phy_address_undeliverable,\n    phy.federal_information_processing_standard_county AS phy_federal_information_processing_standard_county,\n    phy.federal_information_processing_standard_state AS phy_federal_information_processing_standard_state,\n    phy.printer_control_code_begin AS phy_printer_control_code_begin,\n    phy.barcode_zipcode AS phy_barcode_zipcode,\n    phy.barcode_zipcode_plus_4 AS phy_barcode_zipcode_plus_4,\n    phy.delivery_point AS phy_delivery_point,\n    phy.check_digit AS phy_check_digit,\n    phy.printer_control_code_end AS phy_printer_control_code_end,\n    phy.census_region AS phy_region,\n    phy.census_division AS phy_division,\n    phy.census_group AS phy_group,\n    phy.census_tract AS phy_tract,\n    phy.census_suffix AS phy_suffix,\n    phy.census_block_group AS phy_block_group,\n    phy.metropolitan_statistical_area_population AS phy_metropolitan_statistical_area_population,\n    phy.micro_metro_indicator AS phy_micro_metro_indicator,\n    phy.core_based_statistical_area AS phy_core_based_statistical_area_id,\n    cbsa.description AS phy_core_based_statistical_area,\n    phy.core_based_statistical_area_division AS phy_core_based_statistical_area_division,\n    phy.degree_type AS phy_degree_type,\n    phy.birth_year AS phy_birth_year,\n    phy.birth_city AS phy_birth_city,\n    phy.birth_state AS phy_birth_state,\n    phy.birth_country AS phy_birth_country,\n    phy.gender AS phy_gender,\n    phy.telephone_number AS phy_telephone_number,\n    phy.presumed_dead AS phy_presumed_dead,\n    phy.fax_number AS phy_fax_number,\n    phy.type_of_practice AS phy_type_of_practice,\n    top.description AS phy_type_of_practice_description,\n    phy.present_employment AS phy_present_employment_id,\n    pe.description AS phy_present_employment,\n    phy.primary_specialty AS phy_primary_specialty_id,\n    spe.description AS phy_primary_specialty,\n    phy.secondary_specialty AS phy_secondary_specialty,\n    phy.major_professional_activity AS phy_mpa_id,\n    mpa.description AS phy_major_professional_activity,\n    phy.physician_recognition_award_recipient AS phy_physician_recognition_award_recipient,\n    phy.physician_recognition_award_expiration_date AS phy_physician_recognition_award_expiration_date,\n    phy.graduate_medical_education_confirm AS phy_graduate_medical_education_confirm,\n    phy.from_date AS phy_from_date,\n    phy.end_date AS phy_end_date,\n    phy.year_in_program AS phy_year_in_program,\n    phy.post_graduate_year AS phy_post_graduate_year,\n    phy.graduate_medical_education_primary_specialty AS phy_graduate_medical_education_primary_specialty,\n    phy.graduate_medical_education_secondary_specialty AS phy_graduate_medical_education_secondary_specialty,\n    phy.training_type AS phy_training_type,\n    phy.graduate_medical_education_hospital_state AS phy_graduate_medical_education_hospital_state,\n    phy.graduate_medical_education_hospital AS phy_graduate_medical_education_hospital,\n    phy.medical_school_state AS phy_medical_school_state,\n    substr((phy.medical_school_state)::text, 1, 1) AS phy_medical_school_indicator,\n    phy.medical_school AS phy_medical_school,\n    ms.description AS phy_medical_school_name,\n    phy.medical_school_graduation_year AS phy_medical_school_graduation_year,\n    phy.no_contact_type AS phy_no_contact_type,\n    phy.no_web AS phy_no_web,\n    phy.physician_data_restriction_program AS phy_physician_data_restriction_program,\n    phy.physician_data_restriction_program_date AS phy_physician_data_restriction_program_date,\n    phy.polo_address_2 AS phy_polo_address_2,\n    phy.polo_address_1 AS phy_polo_address_1,\n    phy.polo_city AS phy_polo_city,\n    phy.polo_state AS phy_polo_state,\n    phy.polo_zipcode AS phy_polo_zipcode,\n    phy.polo_sector AS phy_polo_sector,\n    phy.polo_carrier_route AS phy_polo_carrier_route,\n    phy.most_recent_former_last_name AS phy_most_recent_former_last_name,\n    phy.most_recent_former_middle_name AS phy_most_recent_former_middle_name,\n    phy.most_recent_former_first_name AS phy_most_recent_former_first_name,\n    phy.next_most_recent_former_last_name AS phy_next_most_recent_former_last_name,\n    phy.next_most_recent_former_middle_name AS phy_next_most_recent_former_middle_name,\n    phy.next_most_recent_former_first_name AS phy_next_most_recent_former_first_name,\n    phy.national_provider_identifier AS phy_national_provider_identifier,\n    phy.party_id AS phy_party_id,\n    phy.entity_id AS phy_entity_id,\n    phy.type AS phy_type,\n    phy.no_release AS phy_no_release,\n    phy.membership_status AS phy_membership_status,\n    phy.has_email AS phy_has_email,\n    bu.name AS aff_business_name,\n    bu.owner_status AS aff_owner_status,\n    bu.profit_status AS aff_profit_status,\n    bu.status_indicator AS aff_status_indicator,\n    bu.electronically_prescribe AS aff_electronically_prescribe,\n    bu.number_of_providers AS aff_physicians_affiliated,\n    bu.class_of_trade_classification_description AS aff_organization_classification,\n    bu.class_of_trade_facility_type_description AS aff_organization_type,\n    bu.class_of_trade_specialty_description AS aff_organization_specialty,\n    bu.physical_state AS aff_physical_state,\n    bu.federal_information_processing_standard_county AS aff_federal_information_processing_standard_county,\n    bu.physical_city AS aff_physical_city,\n    bu.metropolitan_statistical_area AS aff_msa,\n    bu.physical_zipcode AS aff_physical_zipcode,\n    substr((bu.physical_zipcode)::text, 1, 5) AS aff_physician_zipcode_5digits,\n    bu.teaching_hospital AS aff_teaching_hospital,\n    pa.type AS aff_type,\n    pa.description AS aff_hospital_affiliation,\n    pa.group_description AS aff_group_affiliation,\n    pa."primary" AS aff_affiliation_status,\n    pr.first_name AS pro_first_name,\n    pr.middle_name AS pro_middle_name,\n    pr.last_name AS pro_last_name,\n    pr.primary_specialty AS pro_primary_specialty,\n    pr.suffix AS pro_suffix,\n    pr.gender AS pro_gender,\n    pr.national_provider_identifier AS pro_national_provider_identifier,\n    pr.secondary_specialty AS pro_secondary_speciality,\n    rpp.id AS phy_residency_id,\n    zc.metropolitan_statistical_area AS phy_metropolitan_statistical_area,\n    zc.primary_metropolitan_statistical_area AS phy_primary_metropolitan_statistical_area,\n    zc.county_federal_information_processing AS phy_zipcode_county_federal_information_processing,\n    zc.state AS phy_zipcode_state,\n    msa.name AS phy_metropolitan_statistical_area_description,\n    msa.code AS phy_msa_code,\n    msa.type AS phy_msa_type,\n    msa.consolidated_metropolitan_statistical_area,\n    pa.best AS aff_affiliation_best_status\n   FROM ((((((((((((oneview.physician phy\n     LEFT JOIN oneview.type_of_practice top ON (((phy.type_of_practice)::text = (top.id)::text)))\n     LEFT JOIN oneview.present_employment pe ON (((phy.present_employment)::text = (pe.id)::text)))\n     LEFT JOIN oneview.major_professional_activity mpa ON (((phy.major_professional_activity)::text = (mpa.id)::text)))\n     LEFT JOIN oneview.provider_affiliation pa ON (((phy.medical_education_number)::text = (pa.medical_education_number)::text)))\n     LEFT JOIN oneview.business bu ON (((pa.business)::text = (bu.id)::text)))\n     LEFT JOIN oneview.provider pr ON (((phy.medical_education_number)::text = (pr.medical_education_number)::text)))\n     LEFT JOIN oneview.specialty spe ON (((phy.primary_specialty)::text = (spe.id)::text)))\n     LEFT JOIN oneview.core_based_statistical_area cbsa ON (((phy.core_based_statistical_area)::text = (cbsa.id)::text)))\n     LEFT JOIN oneview.residency_program_physician rpp ON (((phy.medical_education_number)::text = (rpp.medical_education_number)::text)))\n     LEFT JOIN oneview.zip_code zc ON (((phy.zipcode)::text = (zc.zip_code)::text)))\n     LEFT JOIN oneview.metropolitan_statistical_area msa ON (((msa.code)::text = (zc.metropolitan_statistical_area)::text)))\n     LEFT JOIN oneview.medical_school ms ON (((substr((ms.id)::text, 1, 3) = (phy.medical_school_state)::text) AND (substr((ms.id)::text, 4, 5) = (phy.medical_school)::text))))\n  ORDER BY phy.medical_education_number',
                with_data=True
            )
    op.replace_entity(oneview_mat_phy_pro_view)

    oneview_mat_phy_view = PGMaterializedView(
                schema="oneview",
                signature="mat_phy_view",
                definition='SELECT phy.medical_education_number AS phy_medical_education_number,\n    phy.address_type AS phy_address_type,\n    phy.mailing_name AS phy_mailing_name,\n    phy.last_name AS phy_last_name,\n    phy.first_name AS phy_first_name,\n    phy.middle_name AS phy_middle_name,\n    phy.name_suffix AS phy_name_suffix,\n    phy.preferred_address_2 AS phy_preferred_address_2,\n    phy.preferred_address_1 AS phy_preferred_address_1,\n    phy.city AS phy_city,\n    phy.state AS phy_state,\n    phy.zipcode AS phy_zipcode,\n    phy.sector AS phy_sector,\n    phy.carrier_route AS phy_carrier_route,\n    phy.address_undeliverable AS phy_address_undeliverable,\n    phy.federal_information_processing_standard_county AS phy_federal_information_processing_standard_county,\n    phy.federal_information_processing_standard_state AS phy_federal_information_processing_standard_state,\n    phy.printer_control_code_begin AS phy_printer_control_code_begin,\n    phy.barcode_zipcode AS phy_barcode_zipcode,\n    phy.barcode_zipcode_plus_4 AS phy_barcode_zipcode_plus_4,\n    phy.delivery_point AS phy_delivery_point,\n    phy.check_digit AS phy_check_digit,\n    phy.printer_control_code_end AS phy_printer_control_code_end,\n    phy.census_region AS phy_region,\n    phy.census_division AS phy_division,\n    phy.census_group AS phy_group,\n    phy.census_tract AS phy_tract,\n    phy.census_suffix AS phy_suffix,\n    phy.census_block_group AS phy_block_group,\n    phy.metropolitan_statistical_area_population AS phy_metropolitan_statistical_area_population,\n    phy.micro_metro_indicator AS phy_micro_metro_indicator,\n    phy.core_based_statistical_area AS phy_core_based_statistical_area_id,\n    cbsa.description AS phy_core_based_statistical_area,\n    phy.core_based_statistical_area_division AS phy_core_based_statistical_area_division,\n    phy.degree_type AS phy_degree_type,\n    phy.birth_year AS phy_birth_year,\n    phy.birth_city AS phy_birth_city,\n    phy.birth_state AS phy_birth_state,\n    phy.birth_country AS phy_birth_country,\n    phy.gender AS phy_gender,\n    phy.telephone_number AS phy_telephone_number,\n    phy.presumed_dead AS phy_presumed_dead,\n    phy.fax_number AS phy_fax_number,\n    phy.type_of_practice AS phy_type_of_practice,\n    top.description AS phy_type_of_practice_description,\n    phy.present_employment AS phy_present_employment_id,\n    pe.description AS phy_present_employment,\n    phy.primary_specialty AS phy_primary_specialty_id,\n    spe.description AS phy_primary_specialty,\n    phy.secondary_specialty AS phy_secondary_specialty,\n    phy.major_professional_activity AS phy_mpa_id,\n    mpa.description AS phy_major_professional_activity,\n    phy.physician_recognition_award_recipient AS phy_physician_recognition_award_recipient,\n    phy.physician_recognition_award_expiration_date AS phy_physician_recognition_award_expiration_date,\n    phy.graduate_medical_education_confirm AS phy_graduate_medical_education_confirm,\n    phy.from_date AS phy_from_date,\n    phy.end_date AS phy_end_date,\n    phy.year_in_program AS phy_year_in_program,\n    phy.post_graduate_year AS phy_post_graduate_year,\n    phy.graduate_medical_education_primary_specialty AS phy_graduate_medical_education_primary_specialty,\n    phy.graduate_medical_education_secondary_specialty AS phy_graduate_medical_education_secondary_specialty,\n    phy.training_type AS phy_training_type,\n    phy.graduate_medical_education_hospital_state AS phy_graduate_medical_education_hospital_state,\n    phy.graduate_medical_education_hospital AS phy_graduate_medical_education_hospital,\n    phy.medical_school_state AS phy_medical_school_state,\n    substr((phy.medical_school_state)::text, 1, 1) AS phy_medical_school_indicator,\n    phy.medical_school AS phy_medical_school,\n    ms.description AS phy_medical_school_name,\n    phy.medical_school_graduation_year AS phy_medical_school_graduation_year,\n    phy.no_contact_type AS phy_no_contact_type,\n    phy.no_web AS phy_no_web,\n    phy.physician_data_restriction_program AS phy_physician_data_restriction_program,\n    phy.physician_data_restriction_program_date AS phy_physician_data_restriction_program_date,\n    phy.polo_address_2 AS phy_polo_address_2,\n    phy.polo_address_1 AS phy_polo_address_1,\n    phy.polo_city AS phy_polo_city,\n    phy.polo_state AS phy_polo_state,\n    phy.polo_zipcode AS phy_polo_zipcode,\n    phy.polo_sector AS phy_polo_sector,\n    phy.polo_carrier_route AS phy_polo_carrier_route,\n    phy.most_recent_former_last_name AS phy_most_recent_former_last_name,\n    phy.most_recent_former_middle_name AS phy_most_recent_former_middle_name,\n    phy.most_recent_former_first_name AS phy_most_recent_former_first_name,\n    phy.next_most_recent_former_last_name AS phy_next_most_recent_former_last_name,\n    phy.next_most_recent_former_middle_name AS phy_next_most_recent_former_middle_name,\n    phy.next_most_recent_former_first_name AS phy_next_most_recent_former_first_name,\n    phy.national_provider_identifier AS phy_national_provider_identifier,\n    phy.party_id AS phy_party_id,\n    phy.entity_id AS phy_entity_id,\n    phy.type AS phy_type,\n    phy.no_release AS phy_no_release,\n    phy.membership_status AS phy_membership_status,\n    phy.has_email AS phy_has_email,\n    bu.name AS aff_business_name,\n    bu.owner_status AS aff_owner_status,\n    bu.profit_status AS aff_profit_status,\n    bu.status_indicator AS aff_status_indicator,\n    bu.electronically_prescribe AS aff_electronically_prescribe,\n    bu.number_of_providers AS aff_physicians_affiliated,\n    bu.class_of_trade_classification_description AS aff_organization_classification,\n    bu.class_of_trade_facility_type_description AS aff_organization_type,\n    bu.class_of_trade_specialty_description AS aff_organization_specialty,\n    bu.physical_state AS aff_physical_state,\n    bu.federal_information_processing_standard_county AS aff_federal_information_processing_standard_county,\n    bu.physical_city AS aff_physical_city,\n    bu.metropolitan_statistical_area AS aff_msa,\n    bu.physical_zipcode AS aff_physical_zipcode,\n    substr((bu.physical_zipcode)::text, 1, 5) AS aff_physician_zipcode_5digits,\n    bu.teaching_hospital AS aff_teaching_hospital,\n    pa.type AS aff_type,\n    pa.description AS aff_hospital_affiliation,\n    pa.group_description AS aff_group_affiliation,\n    pa."primary" AS aff_affiliation_status,\n    rpp.id AS phy_residency_id,\n    zc.metropolitan_statistical_area AS phy_metropolitan_statistical_area,\n    zc.primary_metropolitan_statistical_area AS phy_primary_metropolitan_statistical_area,\n    zc.county_federal_information_processing AS phy_zipcode_county_federal_information_processing,\n    zc.state AS phy_zipcode_state,\n    msa.name AS phy_metropolitan_statistical_area_description,\n    msa.code AS phy_msa_code,\n    msa.type AS phy_msa_type,\n    msa.consolidated_metropolitan_statistical_area,\n    pa.best AS aff_affiliation_best_status\n   FROM (((((((((((oneview.physician phy\n     LEFT JOIN oneview.type_of_practice top ON (((phy.type_of_practice)::text = (top.id)::text)))\n     LEFT JOIN oneview.present_employment pe ON (((phy.present_employment)::text = (pe.id)::text)))\n     LEFT JOIN oneview.major_professional_activity mpa ON (((phy.major_professional_activity)::text = (mpa.id)::text)))\n     LEFT JOIN oneview.provider_affiliation pa ON (((phy.medical_education_number)::text = (pa.medical_education_number)::text)))\n     LEFT JOIN oneview.business bu ON (((pa.business)::text = (bu.id)::text)))\n     LEFT JOIN oneview.specialty spe ON (((phy.primary_specialty)::text = (spe.id)::text)))\n     LEFT JOIN oneview.core_based_statistical_area cbsa ON (((phy.core_based_statistical_area)::text = (cbsa.id)::text)))\n     LEFT JOIN oneview.residency_program_physician rpp ON (((phy.medical_education_number)::text = (rpp.medical_education_number)::text)))\n     LEFT JOIN oneview.zip_code zc ON (((phy.zipcode)::text = (zc.zip_code)::text)))\n     LEFT JOIN oneview.metropolitan_statistical_area msa ON (((msa.code)::text = (zc.metropolitan_statistical_area)::text)))\n     LEFT JOIN oneview.medical_school ms ON (((substr((ms.id)::text, 1, 3) = (phy.medical_school_state)::text) AND (substr((ms.id)::text, 4, 5) = (phy.medical_school)::text))))\n  ORDER BY phy.medical_education_number',
                with_data=True
            )
    op.replace_entity(oneview_mat_phy_view)

    ### Re-add Indexes ###
    op.create_index('mat_phy_aff_zipcode_index', 'mat_phy_view', ['aff_physician_zipcode_5digits'], schema='oneview')
    op.create_index('mat_phy_phy_zipcode_index', 'mat_phy_view', ['phy_zipcode'], schema='oneview')
    op.create_index('mat_phy_phy_polo_zipcode_index', 'mat_phy_view', ['phy_polo_zipcode'], schema='oneview')
    op.create_index('mat_phy_phy_type_of_practice', 'mat_phy_view', ['phy_type_of_practice'], schema='oneview')
    op.create_index('mat_phy_phy_present_employment_id', 'mat_phy_view', ['phy_present_employment_id'], schema='oneview')

    op.create_index('mat_phy_pro_aff_zipcode_index', 'mat_phy_pro_view', ['aff_physician_zipcode_5digits'], schema='oneview')
    op.create_index('mat_phy_pro_phy_zipcode_index', 'mat_phy_pro_view', ['phy_zipcode'], schema='oneview')
    op.create_index('mat_phy_pro_phy_polo_zipcode_index', 'mat_phy_pro_view', ['phy_polo_zipcode'], schema='oneview')
    op.create_index('mat_phy_pro_phy_type_of_practice', 'mat_phy_pro_view', ['phy_type_of_practice'], schema='oneview')
    op.create_index('mat_phy_pro_phy_present_employment_id', 'mat_phy_pro_view', ['phy_present_employment_id'], schema='oneview')

    # ### end Alembic commands ###
