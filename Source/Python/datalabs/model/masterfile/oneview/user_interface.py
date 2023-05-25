""" SQLAlchemy models for OneView UI materialized views """
from   alembic_utils.pg_materialized_view import PGMaterializedView  # pylint: disable=import-error

SCHEMA = 'oneview'


PHYSICIAN_MATERIALIZED_VIEW = PGMaterializedView(
    schema=SCHEMA,
    signature='mat_phy_view',
    with_data=True,
    definition=f'''
SELECT
    phy.medical_education_number AS phy_medical_education_number,
    phy.address_type AS phy_address_type,
    phy.mailing_name AS phy_mailing_name,
    phy.last_name AS phy_last_name,
    phy.first_name AS phy_first_name,
    phy.middle_name AS phy_middle_name,
    phy.name_suffix AS phy_name_suffix,
    phy.preferred_address_2 AS phy_preferred_address_2,
    phy.preferred_address_1 AS phy_preferred_address_1,
    phy.city AS phy_city,
    phy.state AS phy_state,
    phy.zipcode AS phy_zipcode,
    phy.sector AS phy_sector,
    phy.carrier_route AS phy_carrier_route,
    phy.address_undeliverable AS phy_address_undeliverable,
    phy.federal_information_processing_standard_county AS phy_federal_information_processing_standard_county,
    phy.federal_information_processing_standard_state AS phy_federal_information_processing_standard_state,
    phy.printer_control_code_begin AS phy_printer_control_code_begin,
    phy.barcode_zipcode AS phy_barcode_zipcode,
    phy.barcode_zipcode_plus_4 AS phy_barcode_zipcode_plus_4,
    phy.delivery_point AS phy_delivery_point,
    phy.check_digit AS phy_check_digit,
    phy.printer_control_code_end AS phy_printer_control_code_end,
    phy.census_region AS phy_region,
    phy.census_division AS phy_division,
    phy.census_group AS phy_group,
    phy.census_tract AS phy_tract,
    phy.census_suffix AS phy_suffix,
    phy.census_block_group AS phy_block_group,
    phy.metropolitan_statistical_area_population AS phy_metropolitan_statistical_area_population,
    phy.micro_metro_indicator AS phy_micro_metro_indicator,
    phy.core_based_statistical_area AS phy_core_based_statistical_area_id,
    cbsa.description AS phy_core_based_statistical_area,
    phy.core_based_statistical_area_division AS phy_core_based_statistical_area_division,
    phy.degree_type AS phy_degree_type,
    phy.birth_year AS phy_birth_year,
    phy.birth_city AS phy_birth_city,
    phy.birth_state AS phy_birth_state,
    phy.birth_country AS phy_birth_country,
    phy.gender AS phy_gender,
    phy.telephone_number AS phy_telephone_number,
    phy.presumed_dead AS phy_presumed_dead,
    phy.fax_number AS phy_fax_number,
    phy.type_of_practice AS phy_type_of_practice,
    top.description AS phy_type_of_practice_description,
    phy.present_employment AS phy_present_employment_id,
    pe.description AS phy_present_employment,
    phy.primary_specialty AS phy_primary_specialty_id,
    spe.description AS phy_primary_specialty,
    phy.secondary_specialty AS phy_secondary_specialty,
    phy.major_professional_activity AS phy_mpa_id,
    mpa.description AS phy_major_professional_activity,
    phy.physician_recognition_award_recipient AS phy_physician_recognition_award_recipient,
    phy.physician_recognition_award_expiration_date AS phy_physician_recognition_award_expiration_date,
    phy.graduate_medical_education_confirm AS phy_graduate_medical_education_confirm,
    phy.from_date AS phy_from_date,
    phy.end_date AS phy_end_date,
    phy.year_in_program AS phy_year_in_program,
    phy.post_graduate_year AS phy_post_graduate_year,
    phy.graduate_medical_education_primary_specialty AS phy_graduate_medical_education_primary_specialty,
    phy.graduate_medical_education_secondary_specialty AS phy_graduate_medical_education_secondary_specialty,
    phy.training_type AS phy_training_type,
    phy.graduate_medical_education_hospital_state AS phy_graduate_medical_education_hospital_state,
    phy.graduate_medical_education_hospital AS phy_graduate_medical_education_hospital,
    phy.medical_school_state AS phy_medical_school_state,
    substr(phy.medical_school_state::text, 1, 1) AS phy_medical_school_indicator,
    phy.medical_school AS phy_medical_school,
    ms.description AS phy_medical_school_name,
    phy.medical_school_graduation_year AS phy_medical_school_graduation_year,
    phy.no_contact_type AS phy_no_contact_type,
    phy.no_web AS phy_no_web,
    phy.physician_data_restriction_program AS phy_physician_data_restriction_program,
    phy.physician_data_restriction_program_date AS phy_physician_data_restriction_program_date,
    phy.polo_address_2 AS phy_polo_address_2,
    phy.polo_address_1 AS phy_polo_address_1,
    phy.polo_city AS phy_polo_city,
    phy.polo_state AS phy_polo_state,
    phy.polo_zipcode AS phy_polo_zipcode,
    phy.polo_sector AS phy_polo_sector,
    phy.polo_carrier_route AS phy_polo_carrier_route,
    phy.most_recent_former_last_name AS phy_most_recent_former_last_name,
    phy.most_recent_former_middle_name AS phy_most_recent_former_middle_name,
    phy.most_recent_former_first_name AS phy_most_recent_former_first_name,
    phy.next_most_recent_former_last_name AS phy_next_most_recent_former_last_name,
    phy.next_most_recent_former_middle_name AS phy_next_most_recent_former_middle_name,
    phy.next_most_recent_former_first_name AS phy_next_most_recent_former_first_name,
    phy.national_provider_identifier AS phy_national_provider_identifier,
    phy.party_id AS phy_party_id,
    phy.entity_id AS phy_entity_id,
    phy.type AS phy_type,
    phy.no_release AS phy_no_release,
    phy.membership_status AS phy_membership_status,
    phy.has_email AS phy_has_email,
    bu.name AS aff_business_name,
    bu.owner_status AS aff_owner_status,
    bu.profit_status AS aff_profit_status,
    bu.status_indicator AS aff_status_indicator,
    bu.electronically_prescribe AS aff_electronically_prescribe,
    bu.number_of_providers AS aff_physicians_affiliated,
    bu.class_of_trade_classification_description AS aff_organization_classification,
    bu.class_of_trade_facility_type_description AS aff_organization_type,
    bu.class_of_trade_specialty_description AS aff_organization_specialty,
    bu.physical_state AS aff_physical_state,
    bu.federal_information_processing_standard_county AS aff_federal_information_processing_standard_county,
    bu.physical_city AS aff_physical_city,
    bu.metropolitan_statistical_area AS aff_msa,
    bu.physical_zipcode AS aff_physical_zipcode,
    substr(bu.physical_zipcode::text, 1, 5) AS aff_physician_zipcode_5digits,
    bu.teaching_hospital AS aff_teaching_hospital,
    pa.type AS aff_type,
    pa.description AS aff_hospital_affiliation,
    pa.group_description AS aff_group_affiliation,
    pa."primary" AS aff_affiliation_status,
    rpp.id AS phy_residency_id,
    zc.metropolitan_statistical_area AS phy_metropolitan_statistical_area,
    zc.primary_metropolitan_statistical_area AS phy_primary_metropolitan_statistical_area,
    zc.county_federal_information_processing AS phy_zipcode_county_federal_information_processing,
    zc.state AS phy_zipcode_state,
    msa.name AS phy_metropolitan_statistical_area_description,
    msa.code AS phy_msa_code,
    msa.type AS phy_msa_type,
    msa.consolidated_metropolitan_statistical_area,
    pa.best as aff_affiliation_best_status,
    ml.state as phy_license_state
FROM {SCHEMA}.physician phy
    LEFT JOIN {SCHEMA}.type_of_practice top ON phy.type_of_practice::text = top.id::text
    LEFT JOIN {SCHEMA}.present_employment pe ON phy.present_employment::text = pe.id::text
    LEFT JOIN {SCHEMA}.major_professional_activity mpa ON phy.major_professional_activity::text = mpa.id::text
    LEFT JOIN {SCHEMA}.provider_affiliation pa ON phy.medical_education_number::text = pa.medical_education_number::text
    LEFT JOIN {SCHEMA}.business bu ON pa.business::text = bu.id::text
    LEFT JOIN {SCHEMA}.specialty spe ON phy.primary_specialty::text = spe.id::text
    LEFT JOIN {SCHEMA}.core_based_statistical_area cbsa ON phy.core_based_statistical_area::text = cbsa.id::text
    LEFT JOIN {SCHEMA}.residency_program_physician rpp ON phy.medical_education_number::text = rpp.medical_education_number::text
    LEFT JOIN {SCHEMA}.zip_code zc ON phy.zipcode::text = zc.zip_code::text
    LEFT JOIN {SCHEMA}.metropolitan_statistical_area msa ON msa.code::text = zc.metropolitan_statistical_area::text
    LEFT JOIN {SCHEMA}.medical_school ms ON substr(ms.id::text, 1, 3) = phy.medical_school_state::text AND substr(ms.id::text, 4, 5) = phy.medical_school::text
    LEFT JOIN {SCHEMA}.medical_license ml ON phy.medical_education_number::text = ml.medical_education_number::text
ORDER BY phy.medical_education_number;
'''
)


PHYSICIAN_PROVIDER_MATERIALIZED_VIEW = PGMaterializedView(
    schema=SCHEMA,
    signature='mat_phy_pro_view',
    with_data=True,
    definition=f'''
SELECT
    phy.medical_education_number AS phy_medical_education_number,
    phy.address_type AS phy_address_type,
    phy.mailing_name AS phy_mailing_name,
    phy.last_name AS phy_last_name,
    phy.first_name AS phy_first_name,
    phy.middle_name AS phy_middle_name,
    phy.name_suffix AS phy_name_suffix,
    phy.preferred_address_2 AS phy_preferred_address_2,
    phy.preferred_address_1 AS phy_preferred_address_1,
    phy.city AS phy_city,
    phy.state AS phy_state,
    phy.zipcode AS phy_zipcode,
    phy.sector AS phy_sector,
    phy.carrier_route AS phy_carrier_route,
    phy.address_undeliverable AS phy_address_undeliverable,
    phy.federal_information_processing_standard_county AS phy_federal_information_processing_standard_county,
    phy.federal_information_processing_standard_state AS phy_federal_information_processing_standard_state,
    phy.printer_control_code_begin AS phy_printer_control_code_begin,
    phy.barcode_zipcode AS phy_barcode_zipcode,
    phy.barcode_zipcode_plus_4 AS phy_barcode_zipcode_plus_4,
    phy.delivery_point AS phy_delivery_point,
    phy.check_digit AS phy_check_digit,
    phy.printer_control_code_end AS phy_printer_control_code_end,
    phy.census_region AS phy_region,
    phy.census_division AS phy_division,
    phy.census_group AS phy_group,
    phy.census_tract AS phy_tract,
    phy.census_suffix AS phy_suffix,
    phy.census_block_group AS phy_block_group,
    phy.metropolitan_statistical_area_population AS phy_metropolitan_statistical_area_population,
    phy.micro_metro_indicator AS phy_micro_metro_indicator,
    phy.core_based_statistical_area AS phy_core_based_statistical_area_id,
    cbsa.description AS phy_core_based_statistical_area,
    phy.core_based_statistical_area_division AS phy_core_based_statistical_area_division,
    phy.degree_type AS phy_degree_type,
    phy.birth_year AS phy_birth_year,
    phy.birth_city AS phy_birth_city,
    phy.birth_state AS phy_birth_state,
    phy.birth_country AS phy_birth_country,
    phy.gender AS phy_gender,
    phy.telephone_number AS phy_telephone_number,
    phy.presumed_dead AS phy_presumed_dead,
    phy.fax_number AS phy_fax_number,
    phy.type_of_practice AS phy_type_of_practice,
    top.description AS phy_type_of_practice_description,
    phy.present_employment AS phy_present_employment_id,
    pe.description AS phy_present_employment,
    phy.primary_specialty AS phy_primary_specialty_id,
    spe.description AS phy_primary_specialty,
    phy.secondary_specialty AS phy_secondary_specialty,
    phy.major_professional_activity AS phy_mpa_id,
    mpa.description AS phy_major_professional_activity,
    phy.physician_recognition_award_recipient AS phy_physician_recognition_award_recipient,
    phy.physician_recognition_award_expiration_date AS phy_physician_recognition_award_expiration_date,
    phy.graduate_medical_education_confirm AS phy_graduate_medical_education_confirm,
    phy.from_date AS phy_from_date,
    phy.end_date AS phy_end_date,
    phy.year_in_program AS phy_year_in_program,
    phy.post_graduate_year AS phy_post_graduate_year,
    phy.graduate_medical_education_primary_specialty AS phy_graduate_medical_education_primary_specialty,
    phy.graduate_medical_education_secondary_specialty AS phy_graduate_medical_education_secondary_specialty,
    phy.training_type AS phy_training_type,
    phy.graduate_medical_education_hospital_state AS phy_graduate_medical_education_hospital_state,
    phy.graduate_medical_education_hospital AS phy_graduate_medical_education_hospital,
    phy.medical_school_state AS phy_medical_school_state,
    substr(phy.medical_school_state::text, 1, 1) AS phy_medical_school_indicator,
    phy.medical_school AS phy_medical_school,
    ms.description AS phy_medical_school_name,
    phy.medical_school_graduation_year AS phy_medical_school_graduation_year,
    phy.no_contact_type AS phy_no_contact_type,
    phy.no_web AS phy_no_web,
    phy.physician_data_restriction_program AS phy_physician_data_restriction_program,
    phy.physician_data_restriction_program_date AS phy_physician_data_restriction_program_date,
    phy.polo_address_2 AS phy_polo_address_2,
    phy.polo_address_1 AS phy_polo_address_1,
    phy.polo_city AS phy_polo_city,
    phy.polo_state AS phy_polo_state,
    phy.polo_zipcode AS phy_polo_zipcode,
    phy.polo_sector AS phy_polo_sector,
    phy.polo_carrier_route AS phy_polo_carrier_route,
    phy.most_recent_former_last_name AS phy_most_recent_former_last_name,
    phy.most_recent_former_middle_name AS phy_most_recent_former_middle_name,
    phy.most_recent_former_first_name AS phy_most_recent_former_first_name,
    phy.next_most_recent_former_last_name AS phy_next_most_recent_former_last_name,
    phy.next_most_recent_former_middle_name AS phy_next_most_recent_former_middle_name,
    phy.next_most_recent_former_first_name AS phy_next_most_recent_former_first_name,
    phy.national_provider_identifier AS phy_national_provider_identifier,
    phy.party_id AS phy_party_id,
    phy.entity_id AS phy_entity_id,
    phy.type AS phy_type,
    phy.no_release AS phy_no_release,
    phy.membership_status AS phy_membership_status,
    phy.has_email AS phy_has_email,
    bu.name AS aff_business_name,
    bu.owner_status AS aff_owner_status,
    bu.profit_status AS aff_profit_status,
    bu.status_indicator AS aff_status_indicator,
    bu.electronically_prescribe AS aff_electronically_prescribe,
    bu.number_of_providers AS aff_physicians_affiliated,
    bu.class_of_trade_classification_description AS aff_organization_classification,
    bu.class_of_trade_facility_type_description AS aff_organization_type,
    bu.class_of_trade_specialty_description AS aff_organization_specialty,
    bu.physical_state AS aff_physical_state,
    bu.federal_information_processing_standard_county AS aff_federal_information_processing_standard_county,
    bu.physical_city AS aff_physical_city,
    bu.metropolitan_statistical_area AS aff_msa,
    bu.physical_zipcode AS aff_physical_zipcode,
    substr(bu.physical_zipcode::text, 1, 5) AS aff_physician_zipcode_5digits,
    bu.teaching_hospital AS aff_teaching_hospital,
    pa.type AS aff_type,
    pa.description AS aff_hospital_affiliation,
    pa.group_description AS aff_group_affiliation,
    pa."primary" AS aff_affiliation_status,
    pr.first_name AS pro_first_name,
    pr.middle_name AS pro_middle_name,
    pr.last_name AS pro_last_name,
    pr.primary_specialty AS pro_primary_specialty,
    pr.suffix AS pro_suffix,
    pr.gender AS pro_gender,
    pr.national_provider_identifier AS pro_national_provider_identifier,
    pr.secondary_specialty AS pro_secondary_speciality,
    rpp.id AS phy_residency_id,
    zc.metropolitan_statistical_area AS phy_metropolitan_statistical_area,
    zc.primary_metropolitan_statistical_area AS phy_primary_metropolitan_statistical_area,
    zc.county_federal_information_processing AS phy_zipcode_county_federal_information_processing,
    zc.state AS phy_zipcode_state,
    msa.name AS phy_metropolitan_statistical_area_description,
    msa.code AS phy_msa_code,
    msa.type AS phy_msa_type,
    msa.consolidated_metropolitan_statistical_area,
    pa.best as aff_affiliation_best_status,
    ml.state as phy_license_state
FROM {SCHEMA}.physician phy
    LEFT JOIN {SCHEMA}.type_of_practice top ON phy.type_of_practice::text = top.id::text
    LEFT JOIN {SCHEMA}.present_employment pe ON phy.present_employment::text = pe.id::text
    LEFT JOIN {SCHEMA}.major_professional_activity mpa ON phy.major_professional_activity::text = mpa.id::text
    LEFT JOIN {SCHEMA}.provider_affiliation pa ON phy.medical_education_number::text = pa.medical_education_number::text
    LEFT JOIN {SCHEMA}.business bu ON pa.business::text = bu.id::text
    LEFT JOIN {SCHEMA}.provider pr ON phy.medical_education_number::text = pr.medical_education_number::text
    LEFT JOIN {SCHEMA}.specialty spe ON phy.primary_specialty::text = spe.id::text
    LEFT JOIN {SCHEMA}.core_based_statistical_area cbsa ON phy.core_based_statistical_area::text = cbsa.id::text
    LEFT JOIN {SCHEMA}.residency_program_physician rpp ON phy.medical_education_number::text = rpp.medical_education_number::text
    LEFT JOIN {SCHEMA}.zip_code zc ON phy.zipcode::text = zc.zip_code::text
    LEFT JOIN {SCHEMA}.metropolitan_statistical_area msa ON msa.code::text = zc.metropolitan_statistical_area::text
    LEFT JOIN {SCHEMA}.medical_school ms ON substr(ms.id::text, 1, 3) = phy.medical_school_state::text AND substr(ms.id::text, 4, 5) = phy.medical_school::text
    LEFT JOIN {SCHEMA}.medical_license ml ON phy.medical_education_number::text = ml.medical_education_number::text
ORDER BY phy.medical_education_number;
'''
)


FLATTENED_PROVIDER_MATERIALIZED_VIEW = PGMaterializedView(
    schema=SCHEMA,
    signature='provider_flat',
    with_data=True,
    definition=f'''
SELECT
    phy.medical_education_number AS phy_medical_education_number,
    phy.address_type AS phy_address_type,
    phy.mailing_name AS phy_mailing_name,
    phy.last_name AS phy_last_name,
    phy.first_name AS phy_first_name,
    phy.middle_name AS phy_middle_name,
    phy.name_suffix AS phy_name_suffix,
    phy.preferred_address_2 AS phy_preferred_address_2,
    phy.preferred_address_1 AS phy_preferred_address_1,
    phy.city AS phy_city,
    phy.state AS phy_state,
    phy.zipcode AS phy_zipcode,
    phy.sector AS phy_sector,
    phy.carrier_route AS phy_carrier_route,
    phy.address_undeliverable AS phy_address_undeliverable,
    phy.federal_information_processing_standard_county AS phy_federal_information_processing_standard_county,
    phy.federal_information_processing_standard_state AS phy_federal_information_processing_standard_state,
    phy.printer_control_code_begin AS phy_printer_control_code_begin,
    phy.barcode_zipcode AS phy_barcode_zipcode,
    phy.barcode_zipcode_plus_4 AS phy_barcode_zipcode_plus_4,
    phy.delivery_point AS phy_delivery_point,
    phy.check_digit AS phy_check_digit,
    phy.printer_control_code_end AS phy_printer_control_code_end,
    phy.census_region AS phy_region,
    phy.census_division AS phy_division,
    phy.census_group AS phy_group,
    phy.census_tract AS phy_tract,
    phy.census_suffix AS phy_suffix,
    phy.census_block_group AS phy_block_group,
    phy.metropolitan_statistical_area_population AS phy_metropolitan_statistical_area_population,
    phy.micro_metro_indicator AS phy_micro_metro_indicator,
    phy.core_based_statistical_area AS phy_core_based_statistical_area_id,
    cbsa.description AS phy_core_based_statistical_area,
    phy.core_based_statistical_area_division AS phy_core_based_statistical_area_division,
    phy.degree_type AS phy_degree_type,
    phy.birth_year AS phy_birth_year,
    phy.birth_city AS phy_birth_city,
    phy.birth_state AS phy_birth_state,
    phy.birth_country AS phy_birth_country,
    phy.gender AS phy_gender,
    phy.telephone_number AS phy_telephone_number,
    phy.presumed_dead AS phy_presumed_dead,
    phy.fax_number AS phy_fax_number,
    phy.type_of_practice AS phy_type_of_practice,
    top.description AS phy_type_of_practice_description,
    phy.present_employment AS phy_present_employment_id,
    pe.description AS phy_present_employment,
    phy.primary_specialty AS phy_primary_specialty_id,
    spe.description AS phy_primary_specialty,
    phy.secondary_specialty AS phy_secondary_specialty,
    phy.major_professional_activity AS phy_mpa_id,
    mpa.description AS phy_major_professional_activity,
    phy.physician_recognition_award_recipient AS phy_physician_recognition_award_recipient,
    phy.physician_recognition_award_expiration_date AS phy_physician_recognition_award_expiration_date,
    phy.graduate_medical_education_confirm AS phy_graduate_medical_education_confirm,
    phy.from_date AS phy_from_date,
    phy.end_date AS phy_end_date,
    phy.year_in_program AS phy_year_in_program,
    phy.post_graduate_year AS phy_post_graduate_year,
    phy.graduate_medical_education_primary_specialty AS phy_graduate_medical_education_primary_specialty,
    phy.graduate_medical_education_secondary_specialty AS phy_graduate_medical_education_secondary_specialty,
    phy.training_type AS phy_training_type,
    phy.graduate_medical_education_hospital_state AS phy_graduate_medical_education_hospital_state,
    phy.graduate_medical_education_hospital AS phy_graduate_medical_education_hospital,
    phy.medical_school_state AS phy_medical_school_state,
    substr(phy.medical_school_state::text, 1, 1) AS phy_medical_school_indicator,
    phy.medical_school AS phy_medical_school,
    ms.description AS phy_medical_school_name,
    phy.medical_school_graduation_year AS phy_medical_school_graduation_year,
    phy.no_contact_type AS phy_no_contact_type,
    phy.no_web AS phy_no_web,
    phy.physician_data_restriction_program AS phy_physician_data_restriction_program,
    phy.physician_data_restriction_program_date AS phy_physician_data_restriction_program_date,
    phy.polo_address_2 AS phy_polo_address_2,
    phy.polo_address_1 AS phy_polo_address_1,
    phy.polo_city AS phy_polo_city,
    phy.polo_state AS phy_polo_state,
    phy.polo_zipcode AS phy_polo_zipcode,
    phy.polo_sector AS phy_polo_sector,
    phy.polo_carrier_route AS phy_polo_carrier_route,
    phy.most_recent_former_last_name AS phy_most_recent_former_last_name,
    phy.most_recent_former_middle_name AS phy_most_recent_former_middle_name,
    phy.most_recent_former_first_name AS phy_most_recent_former_first_name,
    phy.next_most_recent_former_last_name AS phy_next_most_recent_former_last_name,
    phy.next_most_recent_former_middle_name AS phy_next_most_recent_former_middle_name,
    phy.next_most_recent_former_first_name AS phy_next_most_recent_former_first_name,
    phy.national_provider_identifier AS phy_national_provider_identifier,
    phy.party_id AS phy_party_id,
    phy.entity_id AS phy_entity_id,
    phy.type AS phy_type,
    phy.no_release AS phy_no_release,
    phy.membership_status AS phy_membership_status,
    phy.has_email AS phy_has_email,
    pr.first_name AS pro_first_name,
    pr.middle_name AS pro_middle_name,
    pr.last_name AS pro_last_name,
    pr.primary_specialty AS pro_primary_specialty,
    pr.suffix AS pro_suffix,
    pr.gender AS pro_gender,
    pr.national_provider_identifier AS pro_national_provider_identifier,
    pr.secondary_specialty AS pro_secondary_speciality,
    rpp.id AS phy_residency_id,
    zc.metropolitan_statistical_area AS phy_metropolitan_statistical_area,
    zc.primary_metropolitan_statistical_area AS phy_primary_metropolitan_statistical_area,
    zc.county_federal_information_processing AS phy_zipcode_county_federal_information_processing,
    zc.state AS phy_zipcode_state,
    msa.name AS phy_metropolitan_statistical_area_description,
    msa.code AS phy_msa_code,
    msa.type AS phy_msa_type,
    msa.consolidated_metropolitan_statistical_area
FROM {SCHEMA}.physician phy
    LEFT JOIN {SCHEMA}.type_of_practice top ON phy.type_of_practice::text = top.id::text
    LEFT JOIN {SCHEMA}.present_employment pe ON phy.present_employment::text = pe.id::text
    LEFT JOIN {SCHEMA}.major_professional_activity mpa ON phy.major_professional_activity::text = mpa.id::text
    LEFT JOIN {SCHEMA}.medical_school ms ON substr(ms.id::text, 1, 3) = phy.medical_school_state::text AND substr(ms.id::text, 4, 5) = phy.medical_school::text
    LEFT JOIN {SCHEMA}.provider pr ON phy.medical_education_number::text = pr.medical_education_number::text
    LEFT JOIN {SCHEMA}.specialty spe ON phy.primary_specialty::text = spe.id::text
    LEFT JOIN {SCHEMA}.core_based_statistical_area cbsa ON phy.core_based_statistical_area::text = cbsa.id::text
    LEFT JOIN {SCHEMA}.residency_program_physician rpp ON phy.medical_education_number::text = rpp.medical_education_number::text
    LEFT JOIN (
        SELECT DISTINCT
            zip_code.zip_code,
            zip_code.metropolitan_statistical_area,
            zip_code.primary_metropolitan_statistical_area,
            zip_code.county_federal_information_processing,
            zip_code.state
        FROM {SCHEMA}.zip_code
    ) zc ON phy.zipcode::text = zc.zip_code::text
    LEFT JOIN {SCHEMA}.metropolitan_statistical_area msa ON msa.code::text = zc.metropolitan_statistical_area::text
ORDER BY phy.medical_education_number;
'''
)


FLATTENED_PHYSICIAN_MATERIALIZED_VIEW = PGMaterializedView(
    schema=SCHEMA,
    signature='physician_flat',
    with_data=True,
    definition=f'''
SELECT
    phy.medical_education_number AS phy_medical_education_number,
    phy.address_type AS phy_address_type,
    phy.mailing_name AS phy_mailing_name,
    phy.last_name AS phy_last_name,
    phy.first_name AS phy_first_name,
    phy.middle_name AS phy_middle_name,
    phy.name_suffix AS phy_name_suffix,
    phy.preferred_address_2 AS phy_preferred_address_2,
    phy.preferred_address_1 AS phy_preferred_address_1,
    phy.city AS phy_city,
    phy.state AS phy_state,
    phy.zipcode AS phy_zipcode,
    phy.sector AS phy_sector,
    phy.carrier_route AS phy_carrier_route,
    phy.address_undeliverable AS phy_address_undeliverable,
    phy.federal_information_processing_standard_county AS phy_federal_information_processing_standard_county,
    phy.federal_information_processing_standard_state AS phy_federal_information_processing_standard_state,
    phy.printer_control_code_begin AS phy_printer_control_code_begin,
    phy.barcode_zipcode AS phy_barcode_zipcode,
    phy.barcode_zipcode_plus_4 AS phy_barcode_zipcode_plus_4,
    phy.delivery_point AS phy_delivery_point,
    phy.check_digit AS phy_check_digit,
    phy.printer_control_code_end AS phy_printer_control_code_end,
    phy.census_region AS phy_region,
    phy.census_division AS phy_division,
    phy.census_group AS phy_group,
    phy.census_tract AS phy_tract,
    phy.census_suffix AS phy_suffix,
    phy.census_block_group AS phy_block_group,
    phy.metropolitan_statistical_area_population AS phy_metropolitan_statistical_area_population,
    phy.micro_metro_indicator AS phy_micro_metro_indicator,
    phy.core_based_statistical_area AS phy_core_based_statistical_area_id,
    cbsa.description AS phy_core_based_statistical_area,
    phy.core_based_statistical_area_division AS phy_core_based_statistical_area_division,
    phy.degree_type AS phy_degree_type,
    phy.birth_year AS phy_birth_year,
    phy.birth_city AS phy_birth_city,
    phy.birth_state AS phy_birth_state,
    phy.birth_country AS phy_birth_country,
    phy.gender AS phy_gender,
    phy.telephone_number AS phy_telephone_number,
    phy.presumed_dead AS phy_presumed_dead,
    phy.fax_number AS phy_fax_number,
    phy.type_of_practice AS phy_type_of_practice,
    top.description AS phy_type_of_practice_description,
    phy.present_employment AS phy_present_employment_id,
    pe.description AS phy_present_employment,
    phy.primary_specialty AS phy_primary_specialty_id,
    spe.description AS phy_primary_specialty,
    phy.secondary_specialty AS phy_secondary_specialty,
    phy.major_professional_activity AS phy_mpa_id,
    mpa.description AS phy_major_professional_activity,
    phy.physician_recognition_award_recipient AS phy_physician_recognition_award_recipient,
    phy.physician_recognition_award_expiration_date AS phy_physician_recognition_award_expiration_date,
    phy.graduate_medical_education_confirm AS phy_graduate_medical_education_confirm,
    phy.from_date AS phy_from_date,
    phy.end_date AS phy_end_date,
    phy.year_in_program AS phy_year_in_program,
    phy.post_graduate_year AS phy_post_graduate_year,
    phy.graduate_medical_education_primary_specialty AS phy_graduate_medical_education_primary_specialty,
    phy.graduate_medical_education_secondary_specialty AS phy_graduate_medical_education_secondary_specialty,
    phy.training_type AS phy_training_type,
    phy.graduate_medical_education_hospital_state AS phy_graduate_medical_education_hospital_state,
    phy.graduate_medical_education_hospital AS phy_graduate_medical_education_hospital,
    phy.medical_school_state AS phy_medical_school_state,
    substr(phy.medical_school_state::text, 1, 1) AS phy_medical_school_indicator,
    phy.medical_school AS phy_medical_school,
    ms.description AS phy_medical_school_name,
    phy.medical_school_graduation_year AS phy_medical_school_graduation_year,
    phy.no_contact_type AS phy_no_contact_type,
    phy.no_web AS phy_no_web,
    phy.physician_data_restriction_program AS phy_physician_data_restriction_program,
    phy.physician_data_restriction_program_date AS phy_physician_data_restriction_program_date,
    phy.polo_address_2 AS phy_polo_address_2,
    phy.polo_address_1 AS phy_polo_address_1,
    phy.polo_city AS phy_polo_city,
    phy.polo_state AS phy_polo_state,
    phy.polo_zipcode AS phy_polo_zipcode,
    phy.polo_sector AS phy_polo_sector,
    phy.polo_carrier_route AS phy_polo_carrier_route,
    phy.most_recent_former_last_name AS phy_most_recent_former_last_name,
    phy.most_recent_former_middle_name AS phy_most_recent_former_middle_name,
    phy.most_recent_former_first_name AS phy_most_recent_former_first_name,
    phy.next_most_recent_former_last_name AS phy_next_most_recent_former_last_name,
    phy.next_most_recent_former_middle_name AS phy_next_most_recent_former_middle_name,
    phy.next_most_recent_former_first_name AS phy_next_most_recent_former_first_name,
    phy.national_provider_identifier AS phy_national_provider_identifier,
    phy.party_id AS phy_party_id,
    phy.entity_id AS phy_entity_id,
    phy.type AS phy_type,
    phy.no_release AS phy_no_release,
    phy.membership_status AS phy_membership_status,
    phy.has_email AS phy_has_email,
    rpp.id AS phy_residency_id,
    zc.metropolitan_statistical_area AS phy_metropolitan_statistical_area,
    zc.primary_metropolitan_statistical_area AS phy_primary_metropolitan_statistical_area,
    zc.county_federal_information_processing AS phy_zipcode_county_federal_information_processing,
    zc.state AS phy_zipcode_state,
    msa.name AS phy_metropolitan_statistical_area_description,
    msa.code AS phy_msa_code,
    msa.type AS phy_msa_type,
    msa.consolidated_metropolitan_statistical_area
FROM {SCHEMA}.physician phy
    LEFT JOIN {SCHEMA}.type_of_practice top ON phy.type_of_practice::text = top.id::text
    LEFT JOIN {SCHEMA}.present_employment pe ON phy.present_employment::text = pe.id::text
    LEFT JOIN {SCHEMA}.major_professional_activity mpa ON phy.major_professional_activity::text = mpa.id::text
    LEFT JOIN {SCHEMA}.medical_school ms ON substr(ms.id::text, 1, 3) = phy.medical_school_state::text AND substr(ms.id::text, 4, 5) = phy.medical_school::text
    LEFT JOIN {SCHEMA}.specialty spe ON phy.primary_specialty::text = spe.id::text
    LEFT JOIN {SCHEMA}.core_based_statistical_area cbsa ON phy.core_based_statistical_area::text = cbsa.id::text
    LEFT JOIN {SCHEMA}.residency_program_physician rpp ON phy.medical_education_number::text = rpp.medical_education_number::text
    LEFT JOIN (
        SELECT DISTINCT
            zip_code.zip_code,
            zip_code.metropolitan_statistical_area,
            zip_code.primary_metropolitan_statistical_area,
            zip_code.county_federal_information_processing,
            zip_code.state
        FROM {SCHEMA}.zip_code
    ) zc ON phy.zipcode::text = zc.zip_code::text
    LEFT JOIN {SCHEMA}.metropolitan_statistical_area msa ON msa.code::text = zc.metropolitan_statistical_area::text
ORDER BY phy.medical_education_number;
'''
)


# Defined in Migration Scripts
# Index(f'{SCHEMA}.mat_phy_aff_zipcode_index', f'{SCHEMA}.mat_phy_view.aff_physician_zipcode_5digits')
# Index(f'{SCHEMA}.mat_phy_phy_zipcode_index', f'{SCHEMA}.mat_phy_view.phy_zipcode')
# Index(f'{SCHEMA}.mat_phy_phy_polo_zipcode_index', f'{SCHEMA}.mat_phy_view.phy_polo_zipcode')

# Index(f'{SCHEMA}.mat_phy_pro_aff_zipcode_index', f'{SCHEMA}.mat_phy_pro_view.aff_physician_zipcode_5digits')
# Index(f'{SCHEMA}.mat_phy_pro_phy_zipcode_index', f'{SCHEMA}.mat_phy_pro_view.phy_zipcode')
# Index(f'{SCHEMA}.mat_phy_pro_phy_polo_zipcode_index', f'{SCHEMA}.mat_phy_pro_view.phy_polo_zipcode')

# Index(f'{SCHEMA}.physical_zipcode5', f'{SCHEMA}.business.physical_zipcode5')
