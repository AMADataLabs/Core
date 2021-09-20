""" SQLAlchemy models for OneView """
import sqlalchemy as sa
from   sqlalchemy.ext.declarative import declarative_base

from   datalabs.sqlalchemy import metadata

Base = declarative_base(metadata=metadata())  # pylint: disable=invalid-name


################################################################
# Physician Tables
################################################################

class Physician(Base):
    __tablename__ = 'physician'
    __table_args__ = (
        sa.ForeignKeyConstraint(
            ['federal_information_processing_standard_state',
             'federal_information_processing_standard_county'],
            ['oneview.federal_information_processing_standard_county.state',
             'oneview.federal_information_processing_standard_county.county']
        ),
        {"schema": "oneview"}
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
    membership_year = sa.Column(sa.String)
    type = sa.Column(sa.String)


class ResidencyProgram(Base):
    __tablename__ = 'residency_program'
    __table_args__ = {"schema": "oneview"}

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    specialty = sa.Column(sa.String)
    institution_control = sa.Column(sa.String)
    sequence_number = sa.Column(sa.String)
    federal_code = sa.Column(sa.String)
    region_code = sa.Column(sa.String)
    acgme_accredited = sa.Column(sa.String)
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
    american_osteopathic_association_indicator_program = sa.Column(sa.String)
    osteopathic_principles = sa.Column(sa.Boolean)
    address_1 = sa.Column(sa.String)
    address_2 = sa.Column(sa.String)
    address_3 = sa.Column(sa.String)
    city = sa.Column(sa.String)
    state = sa.Column(sa.String)
    zipcode = sa.Column(sa.String)
    primary_clinical_location = sa.Column(sa.String)
    institution = sa.Column(sa.String, sa.ForeignKey("oneview.residency_program_institution.id"))


class ResidencyProgramPersonnelMember(Base):
    __tablename__ = 'residency_program_personnel_member'
    __table_args__ = {"schema": "oneview"}

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


class ResidencyProgramInstitution(Base):
    __tablename__ = 'residency_program_institution'
    __table_args__ = {"schema": "oneview"}

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    name = sa.Column(sa.String)
    affiliation = sa.Column(sa.String)
    last_update_date = sa.Column(sa.Date)


class Business(Base):
    __tablename__ = 'business'
    __table_args__ = {"schema": "oneview"}

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
    class_of_trade_classification = sa.Column(sa.String)
    class_of_trade_classification_description = sa.Column(sa.String)
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


class Provider(Base):
    __tablename__ = 'provider'
    __table_args__ = {"schema": "oneview"}

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


class ProviderAffiliation(Base):
    __tablename__ = 'provider_affiliation'
    __table_args__ = {"schema": "oneview"}

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

class CredentialingCustomer(Base):
    __tablename__ = 'credentialing_customer'
    __table_args__ = {"schema": "oneview"}

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


class CredentialingOrder(Base):
    __tablename__ = 'credentialing_order'
    __table_args__ = {"schema": "oneview"}

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

class ZipCode(Base):
    __tablename__ = 'zip_code'
    __table_args__ = {"schema": "oneview"}

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


class County(Base):
    __tablename__ = 'county'
    __table_args__ = {"schema": "oneview"}

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


class AreaCode(Base):
    __tablename__ = 'area_code'
    __table_args__ = {"schema": "oneview"}

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    area_code = sa.Column(sa.String, nullable=False)
    prefix = sa.Column(sa.String, nullable=False)
    latitude = sa.Column(sa.String, nullable=False)
    longitude = sa.Column(sa.String, nullable=False)


class Census(Base):
    __tablename__ = 'census'
    __table_args__ = {"schema": "oneview"}

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


class CoreBasedStatisticalAreaMelissa(Base):
    __tablename__ = 'core_based_statistical_area_melissa'
    __table_args__ = {"schema": "oneview"}

    code = sa.Column(sa.String, primary_key=True, nullable=False)
    type = sa.Column(sa.String, nullable=False)
    title = sa.Column(sa.String, nullable=False)
    level = sa.Column(sa.String, nullable=False)
    status = sa.Column(sa.String, nullable=False)


class ZipCodeCoreBasedStatisticalArea(Base):
    __tablename__ = 'zip_code_core_based_statistical_areas'
    __table_args__ = {"schema": "oneview"}

    zip_code = sa.Column(sa.String, primary_key=True, nullable=False)
    core_based_statistical_area = sa.Column(sa.String,
                                            sa.ForeignKey("oneview.core_based_statistical_area_melissa.code"),
                                            nullable=False)
    division = sa.Column(sa.String, nullable=False)


class MetropolitanStatisticalArea(Base):
    __tablename__ = 'metropolitan_statistical_area'
    __table_args__ = {"schema": "oneview"}

    code = sa.Column(sa.String, primary_key=True, nullable=False)
    type = sa.Column(sa.String, nullable=False)
    name = sa.Column(sa.String, nullable=False)
    consolidated_metropolitan_statistical_area = sa.Column(sa.String, nullable=False)
    population = sa.Column(sa.Integer, nullable=False)


class HistoricalResident(Base):
    __tablename__ = 'historical_resident'
    __table_args__ = {"schema": "oneview"}

    medical_education_number = sa.Column(sa.String, primary_key=True, nullable=False)
    institution_code = sa.Column(sa.String, nullable=False)
    specialty = sa.Column(sa.String, nullable=False)
    training_type = sa.Column(sa.String, nullable=False)
    start_year = sa.Column(sa.Integer, nullable=False)
    end_year = sa.Column(sa.Integer, nullable=False)


class IqviaUpdate(Base):
    __tablename__ = 'iqvia_update'
    __table_args__ = {"schema": "oneview"}

    date = sa.Column(sa.Date, unique=True, primary_key=True, nullable=False)


################################################################
# Linking Tables
################################################################

class CredentialingCustomerInstitution(Base):
    __tablename__ = 'credentialing_customer_institution'
    __table_args__ = {"schema": "oneview"}

    id = sa.Column(sa.Integer, primary_key=True)
    customer = sa.Column(sa.Integer, sa.ForeignKey("oneview.credentialing_customer.id"), nullable=False)
    residency_program_institution = sa.Column(sa.String,
                                              sa.ForeignKey("oneview.residency_program_institution.id"),
                                              nullable=False)


class CredentialingCustomerBusiness(Base):
    __tablename__ = 'credentialing_customer_business'
    __table_args__ = {"schema": "oneview"}

    id = sa.Column(sa.Integer, primary_key=True)
    customer = sa.Column(sa.Integer, sa.ForeignKey("oneview.credentialing_customer.id"), nullable=False)
    business = sa.Column(sa.String, sa.ForeignKey("oneview.business.id"), nullable=False)


class ResidencyProgramPhysician(Base):
    __tablename__ = 'residency_program_physician'
    __table_args__ = {"schema": "oneview"}

    id = sa.Column(sa.Integer, primary_key=True)
    personnel_member = sa.Column(sa.String, sa.ForeignKey("oneview.residency_program_personnel_member.id"),
                                 nullable=False, unique=True)
    medical_education_number = sa.Column(sa.String, sa.ForeignKey("oneview.physician.medical_education_number"),
                                         nullable=False, unique=True)


class CorporateParentBusiness(Base):
    __tablename__ = 'corporate_parent_business'
    __table_args__ = {"schema": "oneview"}

    child = sa.Column(sa.String, sa.ForeignKey("oneview.business.id"), primary_key=True, nullable=False)
    parent = sa.Column(sa.String, sa.ForeignKey("oneview.business.id"))


class SubsidiaryOwnerBusiness(Base):
    __tablename__ = 'subsidiary_owner_business'
    __table_args__ = {"schema": "oneview"}

    subsidiary = sa.Column(sa.String, sa.ForeignKey("oneview.business.id"), primary_key=True, nullable=False)
    owner = sa.Column(sa.String, sa.ForeignKey("oneview.business.id"))


################################################################
# Reference Tables
################################################################

class CredentialingProduct(Base):
    __tablename__ = 'credentialing_product'
    __table_args__ = {"schema": "oneview"}

    id = sa.Column(sa.Integer, primary_key=True)
    description = sa.Column(sa.String, nullable=False)


class TypeOfPractice(Base):
    __tablename__ = 'type_of_practice'
    __table_args__ = {"schema": "oneview"}

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    description = sa.Column(sa.String, nullable=False)


class PresentEmployment(Base):
    __tablename__ = 'present_employment'
    __table_args__ = {"schema": "oneview"}

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    description = sa.Column(sa.String, nullable=False)


class MajorProfessionalActivity(Base):
    __tablename__ = 'major_professional_activity'
    __table_args__ = {"schema": "oneview"}

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    description = sa.Column(sa.String, nullable=False)


class FederalInformationProcessingStandardCounty(Base):
    __tablename__ = 'federal_information_processing_standard_county'
    __table_args__ = (
        sa.UniqueConstraint('state', 'county'),
        {"schema": "oneview"}
    )
    id = sa.Column(sa.String, primary_key=True, nullable=False)
    state = sa.Column(sa.String, nullable=False)
    county = sa.Column(sa.String, nullable=False)
    description = sa.Column(sa.String, nullable=False)


class CoreBasedStatisticalArea(Base):
    __tablename__ = 'core_based_statistical_area'
    __table_args__ = {"schema": "oneview"}

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    description = sa.Column(sa.String, nullable=False)


class Specialty(Base):
    __tablename__ = 'specialty'
    __table_args__ = {"schema": "oneview"}

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    description = sa.Column(sa.String, nullable=False)


class State(Base):
    __tablename__ = 'state'
    __table_args__ = {"schema": "oneview"}

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    description = sa.Column(sa.String, nullable=False)


class ClassOfTradeClassification(Base):
    __tablename__ = 'class_of_trade_classification'
    __table_args__ = {"schema": "oneview"}

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    description = sa.Column(sa.String, nullable=False)


class ClassOfTradeSpecialty(Base):
    __tablename__ = 'class_of_trade_specialty'
    __table_args__ = {"schema": "oneview"}

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    description = sa.Column(sa.String, nullable=False)


class ClassOfTradeFacilityType(Base):
    __tablename__ = 'class_of_trade_facility'
    __table_args__ = {"schema": "oneview"}

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    description = sa.Column(sa.String, nullable=False)


class ProviderAffiliationGroup(Base):
    __tablename__ = 'provider_affiliation_group'
    __table_args__ = {"schema": "oneview"}

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    description = sa.Column(sa.String, nullable=False)


class ProviderAffiliationType(Base):
    __tablename__ = 'provider_affiliation_type'
    __table_args__ = {"schema": "oneview"}

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    description = sa.Column(sa.String, nullable=False)


class ProfitStatus(Base):
    __tablename__ = 'profit_status'
    __table_args__ = {"schema": "oneview"}

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    description = sa.Column(sa.String, nullable=False)


class OwnerStatus(Base):
    __tablename__ = 'owner_status'
    __table_args__ = {"schema": "oneview"}

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    description = sa.Column(sa.String, nullable=False)


class AssociationStatus(Base):
    __tablename__ = 'association_status'
    __table_args__ = {"schema": "oneview"}

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    description = sa.Column(sa.String, nullable=False)
