""" SQLAlchemy models for OneView """
from   alembic_utils.pg_view import PGView  # pylint: disable=import-error
import sqlalchemy as sa
from   sqlalchemy.ext.declarative import declarative_base

from   datalabs.sqlalchemy import metadata

BASE = declarative_base(metadata=metadata())
SCHEMA = 'oneview'


################################################################
# Physician Tables
################################################################

class Physician(BASE):
    __tablename__ = 'physician'
    __table_args__ = (
        sa.ForeignKeyConstraint(
            ['federal_information_processing_standard_state',
             'federal_information_processing_standard_county'],
            ['oneview.federal_information_processing_standard_county.state',
             'oneview.federal_information_processing_standard_county.county']
        ),
        {"schema": SCHEMA}
    )

    medical_education_number = sa.Column(sa.String, primary_key=True)
    address_type = sa.Column(sa.String)
    mailing_name = sa.Column(sa.String)
    last_name = sa.Column(sa.String)
    first_name = sa.Column(sa.String)
    middle_name = sa.Column(sa.String)
    name_suffix = sa.Column(sa.String)
    preferred_address_2 = sa.Column(sa.String)
    preferred_address_1 = sa.Column(sa.String)
    city = sa.Column(sa.String)
    state = sa.Column(sa.String, sa.ForeignKey("oneview.state.id"))
    zipcode = sa.Column(sa.String)
    sector = sa.Column(sa.String)
    carrier_route = sa.Column(sa.String)
    address_undeliverable = sa.Column(sa.String)
    federal_information_processing_standard_county = sa.Column(sa.String)
    federal_information_processing_standard_state = sa.Column(sa.String)
    printer_control_code_begin = sa.Column(sa.String)
    barcode_zipcode = sa.Column(sa.String)
    barcode_zipcode_plus_4 = sa.Column(sa.String)
    delivery_point = sa.Column(sa.String)
    check_digit = sa.Column(sa.String)
    printer_control_code_end = sa.Column(sa.String)
    census_region = sa.Column(sa.String)
    census_division = sa.Column(sa.String)
    census_group = sa.Column(sa.String)
    census_tract = sa.Column(sa.String)
    census_suffix = sa.Column(sa.String)
    census_block_group = sa.Column(sa.String)
    metropolitan_statistical_area_population = sa.Column(sa.String)
    micro_metro_indicator = sa.Column(sa.String)
    core_based_statistical_area = sa.Column(sa.String, sa.ForeignKey("oneview.core_based_statistical_area.id"))
    core_based_statistical_area_division = sa.Column(sa.String)
    degree_type = sa.Column(sa.String)
    birth_year = sa.Column(sa.String)
    birth_city = sa.Column(sa.String)
    birth_state = sa.Column(sa.String)
    birth_country = sa.Column(sa.String)
    gender = sa.Column(sa.String)
    telephone_number = sa.Column(sa.String)
    presumed_dead = sa.Column(sa.String)
    fax_number = sa.Column(sa.String)
    type_of_practice = sa.Column(sa.String, sa.ForeignKey("oneview.type_of_practice.id"))
    present_employment = sa.Column(sa.String, sa.ForeignKey("oneview.present_employment.id"))
    primary_specialty = sa.Column(sa.String, sa.ForeignKey("oneview.specialty.id"))
    secondary_specialty = sa.Column(sa.String, sa.ForeignKey("oneview.specialty.id"))
    major_professional_activity = sa.Column(sa.String, sa.ForeignKey("oneview.major_professional_activity.id"))
    physician_recognition_award_recipient = sa.Column(sa.String)
    physician_recognition_award_expiration_date = sa.Column(sa.String)
    graduate_medical_education_confirm = sa.Column(sa.String)
    from_date = sa.Column(sa.String)
    end_date = sa.Column(sa.String)
    year_in_program = sa.Column(sa.String)
    post_graduate_year = sa.Column(sa.String)
    graduate_medical_education_primary_specialty = sa.Column(sa.String)
    graduate_medical_education_secondary_specialty = sa.Column(sa.String)
    training_type = sa.Column(sa.String)
    graduate_medical_education_hospital_state = sa.Column(sa.String)
    graduate_medical_education_hospital = sa.Column(sa.String)
    medical_school_state = sa.Column(sa.String)
    medical_school = sa.Column(sa.String)
    medical_school_graduation_year = sa.Column(sa.String)
    no_contact_type = sa.Column(sa.String)
    no_web = sa.Column(sa.String)
    physician_data_restriction_program = sa.Column(sa.String)
    physician_data_restriction_program_date = sa.Column(sa.String)
    polo_address_2 = sa.Column(sa.String)
    polo_address_1 = sa.Column(sa.String)
    polo_city = sa.Column(sa.String)
    polo_state = sa.Column(sa.String)
    polo_zipcode = sa.Column(sa.String)
    polo_sector = sa.Column(sa.String)
    polo_carrier_route = sa.Column(sa.String)
    most_recent_former_last_name = sa.Column(sa.String)
    most_recent_former_middle_name = sa.Column(sa.String)
    most_recent_former_first_name = sa.Column(sa.String)
    next_most_recent_former_last_name = sa.Column(sa.String)
    next_most_recent_former_middle_name = sa.Column(sa.String)
    next_most_recent_former_first_name = sa.Column(sa.String)
    national_provider_identifier = sa.Column(sa.String)
    party_id = sa.Column(sa.String)
    entity_id = sa.Column(sa.String)
    race_ethnicity = sa.Column(sa.String, nullable=False)
    membership_status = sa.Column(sa.String)
    type = sa.Column(sa.String)


class ResidencyProgram(BASE):
    __tablename__ = 'residency_program'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    specialty = sa.Column(sa.String)
    institution_control = sa.Column(sa.String)
    sequence_number = sa.Column(sa.String)
    federal_code = sa.Column(sa.String)
    region_code = sa.Column(sa.String)
    acgme_accredited = sa.Column(sa.Boolean)
    name = sa.Column(sa.String)
    web_address = sa.Column(sa.String)
    contact_director = sa.Column(sa.Boolean)
    accreditation_status = sa.Column(sa.String)
    accreditation_effective_date = sa.Column(sa.Date)
    initial_accreditation_date = sa.Column(sa.Date)
    accreditation_length = sa.Column(sa.String)
    duration = sa.Column(sa.String)
    government_affiliated = sa.Column(sa.Boolean)
    graduate_medical_education_equivalent_years = sa.Column(sa.String)
    preliminary_years_required = sa.Column(sa.String)
    preliminary_positions_offered = sa.Column(sa.Boolean)
    type = sa.Column(sa.String)
    max_residents_accepted_increase = sa.Column(sa.Integer)
    percent_at_primary_site = sa.Column(sa.String)
    primary_site = sa.Column(sa.String)
    core_program = sa.Column(sa.String)
    medical_records = sa.Column(sa.Boolean)
    official_address = sa.Column(sa.Boolean)
    uses_sfmatch = sa.Column(sa.Boolean)
    other_match_indicator = sa.Column(sa.Boolean)
    other_match = sa.Column(sa.String)
    additional_education_accreditation_length = sa.Column(sa.Boolean)
    last_update_date = sa.Column(sa.Date)
    last_update_type = sa.Column(sa.String)
    american_osteopathic_association_indicator = sa.Column(sa.Boolean)
    american_osteopathic_association_program = sa.Column(sa.String)
    osteopathic_principles = sa.Column(sa.Boolean)
    address_1 = sa.Column(sa.String)
    address_2 = sa.Column(sa.String)
    address_3 = sa.Column(sa.String)
    city = sa.Column(sa.String)
    state = sa.Column(sa.String)
    zipcode = sa.Column(sa.String)
    primary_clinical_location = sa.Column(sa.String)
    institution = sa.Column(sa.String, sa.ForeignKey("oneview.residency_program_institution.id"))


class ResidencyProgramPersonnelMember(BASE):
    __tablename__ = 'residency_program_personnel_member'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    program = sa.Column(sa.String, sa.ForeignKey("oneview.residency_program.id"), nullable=False)
    first_name = sa.Column(sa.String)
    middle_name = sa.Column(sa.String)
    last_name = sa.Column(sa.String)
    suffix_name = sa.Column(sa.String)
    degree_1 = sa.Column(sa.String)
    degree_2 = sa.Column(sa.String)
    degree_3 = sa.Column(sa.String)
    last_update_date = sa.Column(sa.Date)


class ResidencyProgramInstitution(BASE):
    __tablename__ = 'residency_program_institution'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    name = sa.Column(sa.String)
    affiliation = sa.Column(sa.String)
    last_update_date = sa.Column(sa.Date)


class Business(BASE):
    __tablename__ = 'business'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.String, primary_key=True)
    name = sa.Column(sa.String, nullable=False)
    doing_business_as = sa.Column(sa.String)
    iqvia_address_id = sa.Column(sa.String)
    physical_address_1 = sa.Column(sa.String)
    physical_address_2 = sa.Column(sa.String)
    physical_city = sa.Column(sa.String)
    physical_state = sa.Column(sa.String)
    physical_zipcode = sa.Column(sa.String)
    postal_address_1 = sa.Column(sa.String)
    postal_address_2 = sa.Column(sa.String)
    postal_city = sa.Column(sa.String)
    postal_state = sa.Column(sa.String)
    postal_zipcode = sa.Column(sa.String)
    phone = sa.Column(sa.String)
    fax = sa.Column(sa.String)
    website = sa.Column(sa.String)
    latitude = sa.Column(sa.String)
    longitude = sa.Column(sa.String)
    owner_status = sa.Column(sa.String, sa.ForeignKey("oneview.owner_status.id"))
    profit_status = sa.Column(sa.String, sa.ForeignKey("oneview.profit_status.id"))
    primary_class_of_trade = sa.Column(sa.String)
    class_of_trade_classification = sa.Column(sa.String, sa.ForeignKey("oneview.class_of_trade_classification.id"))
    class_of_trade_facility_type = sa.Column(sa.String, sa.ForeignKey("oneview.class_of_trade_facility.id"))
    class_of_trade_facility_type_description = sa.Column(sa.String)
    class_of_trade_specialty = sa.Column(sa.String, sa.ForeignKey("oneview.class_of_trade_specialty.id"))
    class_of_trade_specialty_description = sa.Column(sa.String)
    record_type = sa.Column(sa.String)
    total_licensed_beds = sa.Column(sa.String)
    total_census_beds = sa.Column(sa.String)
    total_staffed_beds = sa.Column(sa.String)
    teaching_hospital = sa.Column(sa.String)
    hospital_care = sa.Column(sa.String)
    metropolitan_statistical_area = sa.Column(sa.String)
    federal_information_processing_standard_state = sa.Column(sa.String)
    federal_information_processing_standard_county = sa.Column(sa.String)
    number_of_providers = sa.Column(sa.String)
    electronic_medical_record = sa.Column(sa.String)
    electronically_prescribe = sa.Column(sa.String)
    pay_for_performance = sa.Column(sa.String)
    deactivation_reason = sa.Column(sa.String)
    replacement_business = sa.Column(sa.String)
    status_indicator = sa.Column(sa.String)
    batch_business_date = sa.Column(sa.Date, sa.ForeignKey("oneview.iqvia_update.date"))


class Provider(BASE):
    __tablename__ = 'provider'
    __table_args__ = {"schema": SCHEMA}

    medical_education_number = sa.Column(sa.String, sa.ForeignKey("oneview.physician.medical_education_number"),
                                         primary_key=True)
    iqvia_provider_id = sa.Column(sa.String)
    first_name = sa.Column(sa.String)
    middle_name = sa.Column(sa.String)
    last_name = sa.Column(sa.String)
    suffix = sa.Column(sa.String)
    designation = sa.Column(sa.String)
    gender = sa.Column(sa.String)
    role = sa.Column(sa.String)
    primary_specialty = sa.Column(sa.String)
    secondary_specialty = sa.Column(sa.String)
    tertiary_specialty = sa.Column(sa.String)
    primary_profession = sa.Column(sa.String)
    primary_profession_description = sa.Column(sa.String)
    unique_physician_identification_number = sa.Column(sa.String)
    national_provider_identifier = sa.Column(sa.String)
    status_description = sa.Column(sa.String)
    batch_business_date = sa.Column(sa.Date, sa.ForeignKey("oneview.iqvia_update.date"))


class ProviderAffiliation(BASE):
    __tablename__ = 'provider_affiliation'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True, nullable=False)
    business = sa.Column(sa.String, sa.ForeignKey("oneview.business.id"))
    medical_education_number = sa.Column(sa.String, sa.ForeignKey("oneview.physician.medical_education_number"))
    type = sa.Column(sa.String, sa.ForeignKey("oneview.provider_affiliation_type.id"))
    description = sa.Column(sa.String)
    primary = sa.Column(sa.String)
    rank = sa.Column(sa.String)
    group = sa.Column(sa.String, sa.ForeignKey("oneview.provider_affiliation_group.id"))
    group_description = sa.Column(sa.String)
    batch_business_date = sa.Column(sa.Date, sa.ForeignKey("oneview.iqvia_update.date"))


################################################################
# Credentialing Tables
################################################################

class CredentialingCustomer(BASE):
    __tablename__ = 'credentialing_customer'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    number = sa.Column(sa.String, nullable=False)
    name = sa.Column(sa.String, nullable=False)
    type = sa.Column(sa.String, nullable=False)
    type_description = sa.Column(sa.String, nullable=False)
    category = sa.Column(sa.String, nullable=False)
    category_description = sa.Column(sa.String, nullable=False)
    current_indicator = sa.Column(sa.String, nullable=False)
    address_1 = sa.Column(sa.String, nullable=False)
    address_2 = sa.Column(sa.String, nullable=False)
    address_3 = sa.Column(sa.String, nullable=False)
    city = sa.Column(sa.String, nullable=False)
    state = sa.Column(sa.String, nullable=False)
    zipcode = sa.Column(sa.String, nullable=False)
    phone_number = sa.Column(sa.String, nullable=False)
    company_name = sa.Column(sa.String, nullable=False)


class CredentialingOrder(BASE):
    __tablename__ = 'credentialing_order'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    customer = sa.Column(sa.Integer, sa.ForeignKey("oneview.credentialing_customer.id"), nullable=False)
    product = sa.Column(sa.Integer, sa.ForeignKey("oneview.credentialing_product.id"), nullable=False)
    number = sa.Column(sa.String, nullable=False)
    medical_education_number = sa.Column(sa.String, sa.ForeignKey("oneview.physician.medical_education_number"),
                                         nullable=False)
    date = sa.Column(sa.String, nullable=False)
    quantity = sa.Column(sa.String, nullable=False)
    unique_physician_identification_number = sa.Column(sa.String, nullable=False)


################################################################
# Statistics Tables
################################################################

class ZipCode(BASE):
    __tablename__ = 'zip_code'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    zip_code = sa.Column(sa.String, nullable=False)
    state = sa.Column(sa.String, nullable=False)
    city = sa.Column(sa.String, nullable=False)
    type = sa.Column(sa.String, nullable=False)
    county_federal_information_processing = sa.Column(sa.String, nullable=False)
    latitude = sa.Column(sa.String, nullable=False)
    longitude = sa.Column(sa.String, nullable=False)
    metropolitan_statistical_area = sa.Column(sa.String, nullable=False)
    primary_metropolitan_statistical_area = sa.Column(sa.String, nullable=False)


class County(BASE):
    __tablename__ = 'county'
    __table_args__ = {"schema": SCHEMA}

    federal_information_processing_standard_code = sa.Column(sa.String, primary_key=True, nullable=False)
    county_name = sa.Column(sa.String, nullable=False)
    state = sa.Column(sa.String, nullable=False)
    time_zone = sa.Column(sa.String, nullable=False)
    county_type = sa.Column(sa.String, nullable=False)
    county_seat = sa.Column(sa.String, nullable=False)
    name_type = sa.Column(sa.String, nullable=False)
    elevation = sa.Column(sa.Integer, nullable=False)
    person_per_household = sa.Column(sa.Integer, nullable=False)
    population = sa.Column(sa.Integer, nullable=False)
    area = sa.Column(sa.Integer, nullable=False)
    households = sa.Column(sa.Integer, nullable=False)
    white = sa.Column(sa.Integer, nullable=False)
    black = sa.Column(sa.Integer, nullable=False)
    hispanic = sa.Column(sa.Integer, nullable=False)
    average_income = sa.Column(sa.String, nullable=False)
    average_house = sa.Column(sa.Integer, nullable=False)


class AreaCode(BASE):
    __tablename__ = 'area_code'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    area_code = sa.Column(sa.String, nullable=False)
    prefix = sa.Column(sa.String, nullable=False)
    latitude = sa.Column(sa.String, nullable=False)
    longitude = sa.Column(sa.String, nullable=False)


class Census(BASE):
    __tablename__ = 'census'
    __table_args__ = {"schema": SCHEMA}

    zip_code = sa.Column(sa.String, primary_key=True, nullable=False)
    population = sa.Column(sa.Integer, nullable=False)
    urban = sa.Column(sa.Integer, nullable=False)
    suburban = sa.Column(sa.Integer, nullable=False)
    farm = sa.Column(sa.Integer, nullable=False)
    non_farm = sa.Column(sa.Integer, nullable=False)
    white = sa.Column(sa.Integer, nullable=False)
    black = sa.Column(sa.Integer, nullable=False)
    indian = sa.Column(sa.Integer, nullable=False)
    asian = sa.Column(sa.Integer, nullable=False)
    hawaiian = sa.Column(sa.Integer, nullable=False)
    race_other = sa.Column(sa.Integer, nullable=False)
    hispanic = sa.Column(sa.Integer, nullable=False)
    age_0_to_4 = sa.Column(sa.Integer, nullable=False)
    age_5_to_9 = sa.Column(sa.Integer, nullable=False)
    age_10_to_14 = sa.Column(sa.Integer, nullable=False)
    age_15_to_17 = sa.Column(sa.Integer, nullable=False)
    age_18_to_19 = sa.Column(sa.Integer, nullable=False)
    age_20 = sa.Column(sa.Integer, nullable=False)
    age_21 = sa.Column(sa.Integer, nullable=False)
    age_22_to_24 = sa.Column(sa.Integer, nullable=False)
    age_25_to_29 = sa.Column(sa.Integer, nullable=False)
    age_30_to_34 = sa.Column(sa.Integer, nullable=False)
    age_35_to_39 = sa.Column(sa.Integer, nullable=False)
    age_40_to_44 = sa.Column(sa.Integer, nullable=False)
    age_45_to_49 = sa.Column(sa.Integer, nullable=False)
    age_50_to_54 = sa.Column(sa.Integer, nullable=False)
    age_55_to_59 = sa.Column(sa.Integer, nullable=False)
    age_60_to_61 = sa.Column(sa.Integer, nullable=False)
    age_65_to_66 = sa.Column(sa.Integer, nullable=False)
    age_67_to_69 = sa.Column(sa.Integer, nullable=False)
    age_70_to_74 = sa.Column(sa.Integer, nullable=False)
    age_75_to_79 = sa.Column(sa.Integer, nullable=False)
    age_80_to_84 = sa.Column(sa.Integer, nullable=False)
    age_85_plus = sa.Column(sa.Integer, nullable=False)
    education_below_9 = sa.Column(sa.Integer, nullable=False)
    education_9_to_12 = sa.Column(sa.Integer, nullable=False)
    education_high_school = sa.Column(sa.Integer, nullable=False)
    education_some_college = sa.Column(sa.Integer, nullable=False)
    education_association = sa.Column(sa.Integer, nullable=False)
    education_bachelor = sa.Column(sa.Integer, nullable=False)
    education_professional = sa.Column(sa.Integer, nullable=False)
    household_income = sa.Column(sa.Integer, nullable=False)
    per_person_income = sa.Column(sa.Integer, nullable=False)
    house_value = sa.Column(sa.Integer, nullable=False)


class CoreBasedStatisticalAreaMelissa(BASE):
    __tablename__ = 'core_based_statistical_area_melissa'
    __table_args__ = {"schema": SCHEMA}

    code = sa.Column(sa.String, primary_key=True, nullable=False)
    type = sa.Column(sa.String, nullable=False)
    title = sa.Column(sa.String, nullable=False)
    level = sa.Column(sa.String, nullable=False)
    status = sa.Column(sa.String, nullable=False)


class ZipCodeCoreBasedStatisticalArea(BASE):
    __tablename__ = 'zip_code_core_based_statistical_areas'
    __table_args__ = {"schema": SCHEMA}

    zip_code = sa.Column(sa.String, primary_key=True, nullable=False)
    core_based_statistical_area = sa.Column(sa.String, nullable=False)
    division = sa.Column(sa.String, nullable=False)


class MetropolitanStatisticalArea(BASE):
    __tablename__ = 'metropolitan_statistical_area'
    __table_args__ = {"schema": SCHEMA}

    code = sa.Column(sa.String, primary_key=True, nullable=False)
    type = sa.Column(sa.String, nullable=False)
    name = sa.Column(sa.String, nullable=False)
    consolidated_metropolitan_statistical_area = sa.Column(sa.String, nullable=False)
    population = sa.Column(sa.Integer, nullable=False)


class HistoricalResident(BASE):
    __tablename__ = 'historical_resident'
    __table_args__ = {"schema": SCHEMA}

    medical_education_number = sa.Column(sa.String, primary_key=True, nullable=False)
    institution_code = sa.Column(sa.String, nullable=False)
    specialty = sa.Column(sa.String, nullable=False)
    training_type = sa.Column(sa.String, nullable=False)
    start_year = sa.Column(sa.Integer, nullable=False)
    end_year = sa.Column(sa.Integer, nullable=False)


class IqviaUpdate(BASE):
    __tablename__ = 'iqvia_update'
    __table_args__ = {"schema": SCHEMA}

    date = sa.Column(sa.Date, unique=True, primary_key=True, nullable=False)


################################################################
# Linking Tables
################################################################

class CredentialingCustomerInstitution(BASE):
    __tablename__ = 'credentialing_customer_institution'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.Integer, primary_key=True)
    customer = sa.Column(sa.Integer, sa.ForeignKey("oneview.credentialing_customer.id"), nullable=False)
    residency_program_institution = sa.Column(sa.String,
                                              sa.ForeignKey("oneview.residency_program_institution.id"),
                                              nullable=False)


class CredentialingCustomerBusiness(BASE):
    __tablename__ = 'credentialing_customer_business'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.Integer, primary_key=True)
    customer = sa.Column(sa.Integer, sa.ForeignKey("oneview.credentialing_customer.id"), nullable=False)
    business = sa.Column(sa.String, sa.ForeignKey("oneview.business.id"), nullable=False)


class ResidencyProgramPhysician(BASE):
    __tablename__ = 'residency_program_physician'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.Integer, primary_key=True)
    personnel_member = sa.Column(sa.String, sa.ForeignKey("oneview.residency_program_personnel_member.id"),
                                 nullable=False, unique=True)
    medical_education_number = sa.Column(sa.String, sa.ForeignKey("oneview.physician.medical_education_number"),
                                         nullable=False, unique=True)


class CorporateParentBusiness(BASE):
    __tablename__ = 'corporate_parent_business'
    __table_args__ = {"schema": SCHEMA}

    child = sa.Column(sa.String, sa.ForeignKey("oneview.business.id"), primary_key=True, nullable=False)
    parent = sa.Column(sa.String, sa.ForeignKey("oneview.business.id"))


class SubsidiaryOwnerBusiness(BASE):
    __tablename__ = 'subsidiary_owner_business'
    __table_args__ = {"schema": SCHEMA}

    subsidiary = sa.Column(sa.String, sa.ForeignKey("oneview.business.id"), primary_key=True, nullable=False)
    owner = sa.Column(sa.String, sa.ForeignKey("oneview.business.id"))


################################################################
# Reference Tables
################################################################

class CredentialingProduct(BASE):
    __tablename__ = 'credentialing_product'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.Integer, primary_key=True)
    description = sa.Column(sa.String, nullable=False)


class TypeOfPractice(BASE):
    __tablename__ = 'type_of_practice'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    description = sa.Column(sa.String, nullable=False)


class PresentEmployment(BASE):
    __tablename__ = 'present_employment'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    description = sa.Column(sa.String, nullable=False)


class MajorProfessionalActivity(BASE):
    __tablename__ = 'major_professional_activity'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    description = sa.Column(sa.String, nullable=False)


class FederalInformationProcessingStandardCounty(BASE):
    __tablename__ = 'federal_information_processing_standard_county'
    __table_args__ = (
        sa.UniqueConstraint('state', 'county'),
        {"schema": SCHEMA}
    )
    id = sa.Column(sa.String, primary_key=True, nullable=False)
    state = sa.Column(sa.String, nullable=False)
    county = sa.Column(sa.String, nullable=False)
    description = sa.Column(sa.String, nullable=False)


class CoreBasedStatisticalArea(BASE):
    __tablename__ = 'core_based_statistical_area'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    description = sa.Column(sa.String, nullable=False)


class Specialty(BASE):
    __tablename__ = 'specialty'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    description = sa.Column(sa.String, nullable=False)


class State(BASE):
    __tablename__ = 'state'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    description = sa.Column(sa.String, nullable=False)


class ClassOfTradeClassification(BASE):
    __tablename__ = 'class_of_trade_classification'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    description = sa.Column(sa.String, nullable=False)


class ClassOfTradeSpecialty(BASE):
    __tablename__ = 'class_of_trade_specialty'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    description = sa.Column(sa.String, nullable=False)


class ClassOfTradeFacilityType(BASE):
    __tablename__ = 'class_of_trade_facility'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    description = sa.Column(sa.String, nullable=False)


class ProviderAffiliationGroup(BASE):
    __tablename__ = 'provider_affiliation_group'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    description = sa.Column(sa.String, nullable=False)


class ProviderAffiliationType(BASE):
    __tablename__ = 'provider_affiliation_type'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    description = sa.Column(sa.String, nullable=False)


class ProfitStatus(BASE):
    __tablename__ = 'profit_status'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    description = sa.Column(sa.String, nullable=False)


class OwnerStatus(BASE):
    __tablename__ = 'owner_status'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    description = sa.Column(sa.String, nullable=False)


class MedicalSchool(BASE):
    __tablename__ = 'medical_school'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    description = sa.Column(sa.String, nullable=False)


### UI Views ###

PHYSICIAN_VIEW = PGView(
    schema=SCHEMA,
    signature='physician_view',
    definition=f'''
SELECT phy.medical_education_number AS phy_medical_education_number,
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
    top.description AS phy_top_description,
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
    phy.medical_school AS phy_medical_school,
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
    phy.race_ethnicity AS phy_race_ethnicity,
    bu.name AS aff_business_name,
    bu.owner_status AS aff_owner_status,
    bu.profit_status AS aff_profit_status,
    bu.status_indicator AS aff_status_indicator,
    bu.electronically_prescribe AS aff_electronically_prescribe,
    bu.number_of_providers AS aff_physicians_affiliated,
    bu.class_of_trade_classification_description AS aff_class_of_trade_classification,
    bu.class_of_trade_facility_type_description AS aff_facility_classification,
    bu.class_of_trade_specialty_description AS aff_business_specialty,
    bu.physical_state AS aff_physical_state,
    bu.federal_information_processing_standard_county AS aff_federal_information_processing_standard_county,
    bu.physical_city AS aff_physical_city,
    bu.metropolitan_statistical_area AS aff_msa,
    bu.physical_zipcode AS aff_physical_zipcode,
    pa.type AS aff_type,
    pa.description AS aff_hospital_affiliation,
    pa.group_description AS aff_group_affiliation,
    pa."primary" AS aff_affiliation_status,
    rpp.id AS phy_residency_id
FROM (((((((({SCHEMA}.physician phy
    LEFT JOIN {SCHEMA}.type_of_practice top ON (((phy.type_of_practice)::text = (top.id)::text)))
    LEFT JOIN {SCHEMA}.present_employment pe ON (((phy.present_employment)::text = (pe.id)::text)))
    LEFT JOIN {SCHEMA}.major_professional_activity mpa ON (((phy.major_professional_activity)::text = (mpa.id)::text)))
    LEFT JOIN {SCHEMA}.provider_affiliation pa ON (((phy.medical_education_number)::text = (pa.medical_education_number)::text)))
    LEFT JOIN {SCHEMA}.business bu ON (((pa.business)::text = (bu.id)::text)))
    LEFT JOIN {SCHEMA}.specialty spe ON (((phy.primary_specialty)::text = (spe.id)::text)))
    LEFT JOIN {SCHEMA}.core_based_statistical_area cbsa ON (((phy.core_based_statistical_area)::text = (cbsa.id)::text)))
    LEFT JOIN {SCHEMA}.residency_program_physician rpp ON (((phy.medical_education_number)::text = (rpp.medical_education_number)::text)))
ORDER BY phy.medical_education_number;'''
)


PHYSICIAN_PROVIDER_VIEW = PGView(
    schema=SCHEMA,
    signature='physician_provider_view',
    definition=f'''
SELECT phy.medical_education_number AS phy_medical_education_number,
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
    top.description AS phy_top_description,
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
    phy.medical_school AS phy_medical_school,
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
    phy.race_ethnicity AS phy_race_ethnicity,
    bu.name AS aff_business_name,
    bu.owner_status AS aff_owner_status,
    bu.profit_status AS aff_profit_status,
    bu.status_indicator AS aff_status_indicator,
    bu.electronically_prescribe AS aff_electronically_prescribe,
    bu.number_of_providers AS aff_physicians_affiliated,
    bu.class_of_trade_classification_description AS aff_class_of_trade_classification,
    bu.class_of_trade_facility_type_description AS aff_facility_classification,
    bu.class_of_trade_specialty_description AS aff_business_specialty,
    bu.physical_state AS aff_physical_state,
    bu.federal_information_processing_standard_county AS aff_federal_information_processing_standard_county,
    bu.physical_city AS aff_physical_city,
    bu.metropolitan_statistical_area AS aff_msa,
    bu.physical_zipcode AS aff_physical_zipcode,
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
    rpp.id AS phy_residency_id
FROM ((((((((({SCHEMA}.physician phy
    LEFT JOIN {SCHEMA}.type_of_practice top ON (((phy.type_of_practice)::text = (top.id)::text)))
    LEFT JOIN {SCHEMA}.present_employment pe ON (((phy.present_employment)::text = (pe.id)::text)))
    LEFT JOIN {SCHEMA}.major_professional_activity mpa ON (((phy.major_professional_activity)::text = (mpa.id)::text)))
    LEFT JOIN {SCHEMA}.provider_affiliation pa ON (((phy.medical_education_number)::text = (pa.medical_education_number)::text)))
    LEFT JOIN {SCHEMA}.business bu ON (((pa.business)::text = (bu.id)::text)))
    LEFT JOIN {SCHEMA}.provider pr ON (((phy.medical_education_number)::text = (pr.medical_education_number)::text)))
    LEFT JOIN {SCHEMA}.specialty spe ON (((phy.primary_specialty)::text = (spe.id)::text)))
    LEFT JOIN {SCHEMA}.core_based_statistical_area cbsa ON (((phy.core_based_statistical_area)::text = (cbsa.id)::text)))
    LEFT JOIN {SCHEMA}.residency_program_physician rpp ON (((phy.medical_education_number)::text = (rpp.medical_education_number)::text)))
ORDER BY phy.medical_education_number;'''
)
