""" SQLAlchemy models for OneView """
import sqlalchemy as sa
from   sqlalchemy.ext.declarative import declarative_base

from   datalabs.sqlalchemy import metadata

Base = declarative_base(metadata=metadata())  # pylint: disable=invalid-name


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
    state = sa.Column(sa.String)
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
    region = sa.Column(sa.String)
    division = sa.Column(sa.String)
    group = sa.Column(sa.String)
    tract = sa.Column(sa.String)
    suffix = sa.Column(sa.String)
    block_group = sa.Column(sa.String)
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
    __table_args__ = {"schema": "oneview"}

    state = sa.Column(sa.String, primary_key=True, nullable=False)
    county = sa.Column(sa.String, primary_key=True, nullable=False)
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


class ResidencyProgram(Base):
    __tablename__ = 'residency_program'
    __table_args__ = {"schema": "oneview"}

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    specialty = sa.Column(sa.String)
    # program_state = sa.Column(sa.String)
    institution_control = sa.Column(sa.String)
    sequence_number = sa.Column(sa.String)
    federal_code = sa.Column(sa.String)
    region_code = sa.Column(sa.String)
    activity_code = sa.Column(sa.String)
    accreditation_council_for_graduate_medical_education_accreditation = sa.Column(sa.String)
    name = sa.Column(sa.String)
    web_address = sa.Column(sa.String)
    old_name = sa.Column(sa.String)
    contact_director = sa.Column(sa.String)
    accreditation_status = sa.Column(sa.String)
    accreditation_effective_date = sa.Column(sa.String)
    initial_accreditation_date = sa.Column(sa.String)
    accreditation_length = sa.Column(sa.String)
    years_offered = sa.Column(sa.String)
    government_affiliation = sa.Column(sa.String)
    graduate_medical_education_equivalent_years = sa.Column(sa.String)
    preliminary_positions_offered = sa.Column(sa.String)
    type = sa.Column(sa.String)
    change_size = sa.Column(sa.String)
    percent_at_primary_site = sa.Column(sa.String)
    primary_site = sa.Column(sa.String)
    core_program = sa.Column(sa.String)
    medical_records = sa.Column(sa.String)
    official_address = sa.Column(sa.String)
    sf_match = sa.Column(sa.String)
    other_match_indicator = sa.Column(sa.String)
    other_match = sa.Column(sa.String)
    additional_education_accreditation_length = sa.Column(sa.String)
    last_update_date = sa.Column(sa.String)
    last_update_type = sa.Column(sa.String)
    american_osteopathic_association_indicator = sa.Column(sa.String)
    american_osteopathic_association_indicator_program_id = sa.Column(sa.String)
    osteopathic_principles = sa.Column(sa.String)
    address_type = sa.Column(sa.String)
    address_1 = sa.Column(sa.String)
    address_2 = sa.Column(sa.String)
    address_3 = sa.Column(sa.String)
    city = sa.Column(sa.String)
    state = sa.Column(sa.String)
    zipcode = sa.Column(sa.String)
    institution = sa.Column(sa.String, sa.ForeignKey("oneview.residency_program_institution.id"))


class ResidencyProgramPersonnelMember(Base):
    __tablename__ = 'residency_program_personnel_member'
    __table_args__ = {"schema": "oneview"}

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    program = sa.Column(sa.String, sa.ForeignKey("oneview.residency_program.id"), nullable=False)
    personnel_type = sa.Column(sa.String)
    aamc_id = sa.Column(sa.String)
    first_name = sa.Column(sa.String)
    middle_name = sa.Column(sa.String)
    last_name = sa.Column(sa.String)
    suffix_name = sa.Column(sa.String)
    degree_1 = sa.Column(sa.String)
    degree_2 = sa.Column(sa.String)
    degree_3 = sa.Column(sa.String)
    phone_number = sa.Column(sa.String)
    email = sa.Column(sa.String)
    last_update_date = sa.Column(sa.String)


class ResidencyProgramInstitution(Base):
    __tablename__ = 'residency_program_institution'
    __table_args__ = {"schema": "oneview"}

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    program = sa.Column(sa.String)
    affiliation = sa.Column(sa.String)
    primary_clinical_location = sa.Column(sa.String)
    last_update_date = sa.Column(sa.String)


class Business(Base):
    __tablename__ = 'business'
    __table_args__ = {"schema": "oneview"}

    id = sa.Column(sa.String, primary_key=True)
    name = sa.Column(sa.String, nullable=False)
    doing_business_as = sa.Column(sa.String)
    address_id = sa.Column(sa.String)
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
    owner_status = sa.Column(sa.String)
    profit_status = sa.Column(sa.String)
    primary_class_of_trade = sa.Column(sa.String)
    class_of_trade_classification = sa.Column(sa.String)
    class_of_trade_classification_description = sa.Column(sa.String)
    class_of_trade_facility_type = sa.Column(sa.String)
    class_of_trade_facility_type_description = sa.Column(sa.String)
    class_of_trade_specialty = sa.Column(sa.String)
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
    corporate_parent_business = sa.Column(sa.String)
    corporate_parent_business_name = sa.Column(sa.String)
    owner_subsidiary = sa.Column(sa.String, sa.ForeignKey("oneview.owner_subsidiary.id"))
    electronic_medical_record = sa.Column(sa.String)
    electronically_prescribe = sa.Column(sa.String)
    pay_for_performance = sa.Column(sa.String)
    deactivation_reason = sa.Column(sa.String)
    replacement_business = sa.Column(sa.String)
    status_indicator = sa.Column(sa.String)
    batch_business_date = sa.Column(sa.String)


class OwnerSubsidiary(Base):
    __tablename__ = 'owner_subsidiary'
    __table_args__ = {"schema": "oneview"}

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    name = sa.Column(sa.String, nullable=False)


class Provider(Base):
    __tablename__ = 'provider'
    __table_args__ = {"schema": "oneview"}

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    medical_education_number = sa.Column(sa.String, sa.ForeignKey("oneview.physician.medical_education_number"))
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
    universal_provider_identification = sa.Column(sa.String)
    national_provider_identifier = sa.Column(sa.String)
    status_description = sa.Column(sa.String)
    batch_business_date = sa.Column(sa.String)


class ProviderAffiliation(Base):
    __tablename__ = 'provider_affiliation'
    __table_args__ = {"schema": "oneview"}

    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True, nullable=False)
    business = sa.Column(sa.String, sa.ForeignKey("oneview.business.id"))
    provider = sa.Column(sa.String, sa.ForeignKey("oneview.provider.id"))
    type = sa.Column(sa.String)
    description = sa.Column(sa.String)
    primary = sa.Column(sa.String)
    rank = sa.Column(sa.String)
    group = sa.Column(sa.String)
    group_description = sa.Column(sa.String)
    batch_business_date = sa.Column(sa.String)


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


class CredentialingProduct(Base):
    __tablename__ = 'credentialing_product'
    __table_args__ = {"schema": "oneview"}

    id = sa.Column(sa.Integer, primary_key=True)
    description = sa.Column(sa.String, nullable=False)


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
    person_id = sa.Column(sa.String, nullable=False)
    unique_physician_identification_number = sa.Column(sa.String, nullable=False)
    first_name = sa.Column(sa.String)
    middle_name = sa.Column(sa.String)
    last_name = sa.Column(sa.String)
    suffix = sa.Column(sa.String)
    former_name = sa.Column(sa.String)


class PhysicianRaceEthnicity(Base):
    __tablename__ = 'physician_race_ethnicity'
    __table_args__ = {"schema": "oneview"}

    medical_education_number = sa.Column(sa.String, sa.ForeignKey("oneview.physician.medical_education_number"),
                                         primary_key=True, nullable=False)
    race_ethnicity = sa.Column(sa.String, nullable=False)
    gender = sa.Column(sa.String, nullable=False)
    current_person_type = sa.Column(sa.String, nullable=False)


class CredentialingCustomerInstitution(Base):
    __tablename__ = 'credentialing_customer_institution'
    __table_args__ = {"schema": "oneview"}

    customer = sa.Column(sa.Integer, sa.ForeignKey("oneview.credentialing_customer.id"), primary_key=True,
                         nullable=False)
    residency_program_institution = sa.Column(sa.String,
                                              sa.ForeignKey("oneview.residency_program_institution.id"),
                                              nullable=False)


class CredentialingCustomerBusiness(Base):
    __tablename__ = 'credentialing_customer_business'
    __table_args__ = {"schema": "oneview"}

    customer = sa.Column(sa.Integer, sa.ForeignKey("oneview.credentialing_customer.id"), primary_key=True,
                         nullable=False)
    business = sa.Column(sa.String, sa.ForeignKey("oneview.business.id"), nullable=False)


class ResidencyProgramPhysician(Base):
    __tablename__ = 'residency_program_physician'
    __table_args__ = {"schema": "oneview"}

    personnel_member = sa.Column(sa.String, sa.ForeignKey("oneview.residency_program_personnel_member.id"),
                                 primary_key=True, nullable=False)
    medical_education_number = sa.Column(sa.String, sa.ForeignKey("oneview.physician.medical_education_number"),
                                         nullable=False)
