""" SQLAlchemy models for OneView """
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base

from datalabs.sqlalchemy import metadata

Base = declarative_base(metadata=metadata())  # pylint: disable=invalid-name


class Physician(Base):
    __tablename__ = 'physician'
    __table_args__ = {"schema": "oneview"}

    medical_education_number = sa.Column(sa.Integer, primary_key=True)
    address_type = sa.Column(sa.String, nullable=False)
    mailing_name = sa.Column(sa.String, nullable=False)
    last_name = sa.Column(sa.String, nullable=False)
    first_name = sa.Column(sa.String, nullable=False)
    middle_name = sa.Column(sa.String, nullable=False)
    name_suffix = sa.Column(sa.String, nullable=False)
    preferred_address_2 = sa.Column(sa.String, nullable=False)
    preferred_address_1 = sa.Column(sa.String, nullable=False)
    city = sa.Column(sa.String, nullable=False)
    state = sa.Column(sa.String, nullable=False)
    zipcode = sa.Column(sa.String, nullable=False)
    sector = sa.Column(sa.String, nullable=False)
    carrier_route = sa.Column(sa.String, nullable=False)
    address_undeliverable = sa.Column(sa.String, nullable=False)
    federal_information_processing_standard_county = sa.Column(sa.String, nullable=False)
    federal_information_processing_standard_state = sa.Column(sa.String, nullable=False)
    printer_control_code_begin = sa.Column(sa.String, nullable=False)
    barcode_zipcode = sa.Column(sa.String, nullable=False)
    barcode_zipcode_plus_4 = sa.Column(sa.String, nullable=False)
    delivery_point = sa.Column(sa.String, nullable=False)
    check_digit = sa.Column(sa.String, nullable=False)
    printer_control_code_end = sa.Column(sa.String, nullable=False)
    region = sa.Column(sa.String, nullable=False)
    division = sa.Column(sa.String, nullable=False)
    group = sa.Column(sa.String, nullable=False)
    tract = sa.Column(sa.String, nullable=False)
    suffix = sa.Column(sa.String, nullable=False)
    block_group = sa.Column(sa.String, nullable=False)
    metropolitan_statistical_area_population = sa.Column(sa.String, nullable=False)
    micro_metro_indicator = sa.Column(sa.String, nullable=False)
    core_based_statistical_area = sa.Column(sa.String, nullable=False)
    core_based_statistical_area_division = sa.Column(sa.String, nullable=False)
    degree_type = sa.Column(sa.String, nullable=False)
    birth_year = sa.Column(sa.String, nullable=False)
    birth_city = sa.Column(sa.String, nullable=False)
    birth_state = sa.Column(sa.String, nullable=False)
    birth_country = sa.Column(sa.String, nullable=False)
    gender = sa.Column(sa.String, nullable=False)
    telephone_number = sa.Column(sa.String, nullable=False)
    presumed_dead = sa.Column(sa.String, nullable=False)
    fax_number = sa.Column(sa.String, nullable=False)
    type_of_practice_code = sa.Column(sa.String, nullable=False)
    present_employment = sa.Column(sa.String, nullable=False)
    primary_specialty = sa.Column(sa.String, nullable=False)
    secondary_specialty = sa.Column(sa.String, nullable=False)
    major_professional_activity = sa.Column(sa.String, nullable=False)
    physician_recognition_award_recipient = sa.Column(sa.String, nullable=False)
    physician_recognition_award_expiration_date = sa.Column(sa.String, nullable=False)
    graduate_medical_education_confirm = sa.Column(sa.String, nullable=False)
    from_date = sa.Column(sa.String, nullable=False)
    end_date = sa.Column(sa.String, nullable=False)
    year_in_program = sa.Column(sa.String, nullable=False)
    post_graduate_year = sa.Column(sa.String, nullable=False)
    graduate_medical_education_primary_specialty = sa.Column(sa.String, nullable=False)
    graduate_medical_education_secondary_specialty = sa.Column(sa.String, nullable=False)
    training_type = sa.Column(sa.String, nullable=False)
    graduate_medical_education_hospital_state = sa.Column(sa.String, nullable=False)
    graduate_medical_education_hospital = sa.Column(sa.String, nullable=False)
    medical_school_state = sa.Column(sa.String, nullable=False)
    medical_school = sa.Column(sa.String, nullable=False)
    medical_school_graduation_year = sa.Column(sa.String, nullable=False)
    no_contact_type = sa.Column(sa.String, nullable=False)
    no_web = sa.Column(sa.String, nullable=False)
    physician_data_restriction_program = sa.Column(sa.String, nullable=False)
    physician_data_restriction_program_date = sa.Column(sa.String, nullable=False)
    polo_address_2 = sa.Column(sa.String, nullable=False)
    polo_address_1 = sa.Column(sa.String, nullable=False)
    polo_city = sa.Column(sa.String, nullable=False)
    polo_state = sa.Column(sa.String, nullable=False)
    polo_zipcode = sa.Column(sa.String, nullable=False)
    polo_sector = sa.Column(sa.String, nullable=False)
    polo_carrier_route = sa.Column(sa.String, nullable=False)
    most_recent_former_last_name = sa.Column(sa.String, nullable=False)
    most_recent_former_middle_name = sa.Column(sa.String, nullable=False)
    most_recent_former_first_name = sa.Column(sa.String, nullable=False)
    next_most_recent_former_last_name = sa.Column(sa.String, nullable=False)
    next_most_recent_former_middle_name = sa.Column(sa.String, nullable=False)
    next_most_recent_former_first_name = sa.Column(sa.String, nullable=False)
    npi = sa.Column(sa.Integer, nullable=False)


class ResidencyProgram(Base):
    __tablename__ = 'residency_program_addresses'
    __table_args__ = {"schema": "oneview"}

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False)
    web_address = sa.Column(sa.String, nullable=False)
    old_name = sa.Column(sa.String, nullable=False)
    address_type = sa.Column(sa.String, nullable=False)
    address_1 = sa.Column(sa.String, nullable=False)
    address_2 = sa.Column(sa.String, nullable=False)
    address_3 = sa.Column(sa.String, nullable=False)
    city = sa.Column(sa.String, nullable=False)
    state = sa.Column(sa.String, nullable=False)
    zipcode = sa.Column(sa.String, nullable=False)
    institution = sa.Column(sa.Integer, sa.ForeignKey("oneview.residency_program_institution.id"), nullable=False)


class ResidencyProgramPersonnelMember(Base):
    __tablename__ = 'residency_program_personnel_member'
    __table_args__ = {"schema": "oneview"}

    id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    program = sa.Column(sa.Integer, sa.ForeignKey("oneview.residency_program_addresses.id"), nullable=False)
    personnel_type = sa.Column(sa.String, nullable=False)
    aamc_id = sa.Column(sa.Integer, nullable=False, unique=True)
    first_name = sa.Column(sa.String, nullable=False)
    middle_name = sa.Column(sa.String, nullable=False)
    last_name = sa.Column(sa.String, nullable=False)
    suffix_name = sa.Column(sa.String, nullable=False)
    degree_1 = sa.Column(sa.String, nullable=False)
    degree_2 = sa.Column(sa.String, nullable=False)
    degree_3 = sa.Column(sa.String, nullable=False)
    phone_number = sa.Column(sa.String, nullable=False)
    email = sa.Column(sa.String, nullable=False)


class ResidencyProgramInstitution(Base):
    __tablename__ = 'residency_program_institution'
    __table_args__ = {"schema": "oneview"}

    id = sa.Column(sa.Integer, primary_key=True, nullable=False)


class Business(Base):
    __tablename__ = 'business'
    __table_args__ = {"schema": "oneview"}

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False)
    doing_business_as = sa.Column(sa.String, nullable=False)
    physical_address_1 = sa.Column(sa.String, nullable=False)
    physical_address_2 = sa.Column(sa.String, nullable=False)
    physical_city = sa.Column(sa.String, nullable=False)
    physical_state = sa.Column(sa.String, nullable=False)
    physical_zipcode = sa.Column(sa.String, nullable=False)
    postal_address_1 = sa.Column(sa.String, nullable=False)
    postal_address_2 = sa.Column(sa.String, nullable=False)
    postal_city = sa.Column(sa.String, nullable=False)
    postal_state = sa.Column(sa.String, nullable=False)
    postal_zipcode = sa.Column(sa.String, nullable=False)
    phone = sa.Column(sa.String, nullable=False)
    fax = sa.Column(sa.String, nullable=False)
    website = sa.Column(sa.String, nullable=False)
    owner_status = sa.Column(sa.String, nullable=False)
    profit_status = sa.Column(sa.String, nullable=False)


class Provider(Base):
    __tablename__ = 'provider'
    __table_args__ = {"schema": "oneview"}

    id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    medical_education_number = sa.Column(sa.Integer, sa.ForeignKey("oneview.physician.medical_education_number"),
                                         nullable=False)
    first_name = sa.Column(sa.String, nullable=False)
    middle_name = sa.Column(sa.String, nullable=False)
    last_name = sa.Column(sa.String, nullable=False)
    suffix = sa.Column(sa.String, nullable=False)
    designation = sa.Column(sa.String, nullable=False)
    gender = sa.Column(sa.String, nullable=False)
    role = sa.Column(sa.String, nullable=False)
    primary_specialty = sa.Column(sa.String, nullable=False)
    secondary_specialty = sa.Column(sa.String, nullable=False)
    tertiary_specialty = sa.Column(sa.String, nullable=False)
    primary_profession = sa.Column(sa.String, nullable=False)
    primary_profession_description = sa.Column(sa.String, nullable=False)
    status_description = sa.Column(sa.String, nullable=False)


class ProviderAffiliation(Base):
    __tablename__ = 'provider_affiliation'
    __table_args__ = {"schema": "oneview"}

    id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    business = sa.Column(sa.Integer, sa.ForeignKey("oneview.business.id"))
    provider = sa.Column(sa.Integer, sa.ForeignKey("oneview.provider.id"))
    description = sa.Column(sa.String, nullable=False)
    primary = sa.Column(sa.Boolean, default=False)
    rank = sa.Column(sa.String, nullable=False)


class CredentialingCustomer(Base):
    __tablename__ = 'credentialing_customer'
    __table_args__ = {"schema": "oneview"}

    id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    number = sa.Column(sa.String, nullable=False)
    isell_username = sa.Column(sa.String, nullable=False)
    name = sa.Column(sa.String, nullable=False)
    type = sa.Column(sa.String, nullable=False)
    type_description = sa.Column(sa.String, nullable=False)
    category = sa.Column(sa.String, nullable=False)
    category_description = sa.Column(sa.String, nullable=False)
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
    __tablename__ = 'credentialing_order '
    __table_args__ = {"schema": "oneview"}

    id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    customer = sa.Column(sa.Integer, sa.ForeignKey("oneview.credentialing_customer.id"), nullable=False)
    product = sa.Column(sa.Integer, sa.ForeignKey("oneview.credentialing_product.id"), nullable=False)
    number = sa.Column(sa.String, nullable=False)
    medical_education_number = sa.Column(sa.Integer, sa.ForeignKey("oneview.physician.medical_education_number"),
                                         nullable=False)
    date = sa.Column(sa.String, nullable=False)


class Ethnicity(Base):
    __tablename__ = 'ethnicity'
    __table_args__ = {"schema": "oneview"}

    id = sa.Column(sa.Integer, primary_key=True, nullable=False, unique=True)
    description = sa.Column(sa.String, nullable=False)


class PhysicianEthnicity(Base):
    __tablename__ = 'physician_ethnicity'
    __table_args__ = {"schema": "oneview"}

    medical_education_number = sa.Column(sa.Integer, sa.ForeignKey("oneview.physician.medical_education_number"),
                                         primary_key=True, nullable=False)
    ethnicity = sa.Column(sa.Integer, sa.ForeignKey("oneview.ethnicity.id"), nullable=False)


class CredentialingCustomerInstitution(Base):
    __tablename__ = 'credentialing_customer_institution'
    __table_args__ = {"schema": "oneview"}

    customer = sa.Column(sa.Integer, sa.ForeignKey("oneview.credentialing_customer.id"), primary_key=True,
                         nullable=False)
    residency_program_institution = sa.Column(sa.Integer,
                                              sa.ForeignKey("oneview.residency_program_institution.id"),
                                              nullable=False)


class CredentialingCustomerBusiness(Base):
    __tablename__ = 'credentialing_customer_business'
    __table_args__ = {"schema": "oneview"}

    customer = sa.Column(sa.Integer, sa.ForeignKey("oneview.credentialing_customer.id"), primary_key=True,
                         nullable=False)
    business = sa.Column(sa.Integer, sa.ForeignKey("oneview.business.id"), nullable=False)


class ResidencyProgramPhysician(Base):
    __tablename__ = 'medical_education_physician'
    __table_args__ = {"schema": "oneview"}

    personnel_member = sa.Column(sa.Integer, sa.ForeignKey("oneview.residency_program_personnel_member.id"),
                                 primary_key=True, nullable=False)
    medical_education_number = sa.Column(sa.Integer, sa.ForeignKey("oneview.physician.medical_education_number"),
                                         nullable=False)
