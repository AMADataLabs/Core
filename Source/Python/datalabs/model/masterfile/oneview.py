""" SQLAlchemy models for OneView """
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base

from datalabs.sqlalchemy import metadata

Base = declarative_base(metadata=metadata())  # pylint: disable=invalid-name


class Physician(Base):
    __tablename__ = 'physician'
    __table_args__ = {"schema": "oneview"}

    medical_education_number = sa.Column(sa.Integer, primary_key=True)
    entity_id = sa.Column(sa.String, nullable=False)
    party_id = sa.Column(sa.String, nullable=False)
    last_name = sa.Column(sa.String, nullable=False)
    first_name = sa.Column(sa.String, nullable=False)
    middle_name = sa.Column(sa.String, nullable=False)
    name_suffix = sa.Column(sa.String, nullable=False)
    address_type = sa.Column(sa.String, nullable=False)
    address_usage = sa.Column(sa.String, nullable=False)
    address_begin_date = sa.Column(sa.String, nullable=False)
    address_end_date = sa.Column(sa.String, nullable=False)
    address_usage_source = sa.Column(sa.String, nullable=False)
    address_line_1 = sa.Column(sa.String, nullable=False)
    address_line_2 = sa.Column(sa.String, nullable=False)
    address_line_3 = sa.Column(sa.String, nullable=False)
    city = sa.Column(sa.String, nullable=False)
    state = sa.Column(sa.String, nullable=False)
    zipcode = sa.Column(sa.String, nullable=False)
    zipcode_plus_4 = sa.Column(sa.String, nullable=False)
    address_undeliverable_flag = sa.Column(sa.String, nullable=False)
    degree = sa.Column(sa.String, nullable=False)
    birth_year = sa.Column(sa.String, nullable=False)
    birth_city = sa.Column(sa.String, nullable=False)
    birth_state = sa.Column(sa.String, nullable=False)
    birth_country = sa.Column(sa.String, nullable=False)
    gender = sa.Column(sa.String, nullable=False)
    race_ethnicity = sa.Column(sa.String, nullable=False)
    mortality_indicator = sa.Column(sa.String, nullable=False)
    death_date = sa.Column(sa.String, nullable=False)
    communication_restriction_flags = sa.Column(sa.String, nullable=False)
    perm_foreign_flag = sa.Column(sa.String, nullable=False)
    cut_flag = sa.Column(sa.String, nullable=False)
    telephone_number = sa.Column(sa.String, nullable=False)
    telephone_number_begin_date = sa.Column(sa.String, nullable=False)
    telephone_number_end_date = sa.Column(sa.String, nullable=False)
    telephone_number_source = sa.Column(sa.String, nullable=False)
    fax_number = sa.Column(sa.String, nullable=False)
    fax_number_begin_date = sa.Column(sa.String, nullable=False)
    fax_number_end_date = sa.Column(sa.String, nullable=False)
    fax_number_source = sa.Column(sa.String, nullable=False)
    email_address = sa.Column(sa.String, nullable=False)
    email_address_begin_date = sa.Column(sa.String, nullable=False)
    email_address_end_date = sa.Column(sa.String, nullable=False)
    email_address_usage_source = sa.Column(sa.String, nullable=False)
    type_of_practice = sa.Column(sa.String, nullable=False)
    present_employment = sa.Column(sa.String, nullable=False)
    major_professional_activity = sa.Column(sa.String, nullable=False)
    primary_speciality = sa.Column(sa.String, nullable=False)
    secondary_speciality = sa.Column(sa.String, nullable=False)
    state_license_number = sa.Column(sa.String, nullable=False)
    state_license_state = sa.Column(sa.String, nullable=False)
    state_license_issue_date = sa.Column(sa.String, nullable=False)
    state_license_expiration_date = sa.Column(sa.String, nullable=False)
    state_license_renewal_date = sa.Column(sa.String, nullable=False)
    state_license_status = sa.Column(sa.String, nullable=False)
    state_license_type = sa.Column(sa.String, nullable=False)
    state_license_degree = sa.Column(sa.String, nullable=False)
    dea_number = sa.Column(sa.String, nullable=False)
    dea_status = sa.Column(sa.String, nullable=False)
    dea_expiration_date = sa.Column(sa.String, nullable=False)
    npi_number = sa.Column(sa.Integer, nullable=False)
    npi_enumeration_date = sa.Column(sa.String, nullable=False)
    abms_id = sa.Column(sa.String, nullable=False)
    abms_certificate_id = sa.Column(sa.String, nullable=False)
    abms_issue_date = sa.Column(sa.String, nullable=False)
    abms_expiration_date = sa.Column(sa.String, nullable=False)
    abms_reverification_date = sa.Column(sa.String, nullable=False)
    abms_record_type = sa.Column(sa.String, nullable=False)
    medical_school = sa.Column(sa.String, nullable=False)
    medical_school_enrollment_status = sa.Column(sa.String, nullable=False)
    medical_school_graduation_year = sa.Column(sa.String, nullable=False)
    gme_hospital = sa.Column(sa.String, nullable=False)
    gme_primary_speciality = sa.Column(sa.String, nullable=False)
    gme_begin_date = sa.Column(sa.String, nullable=False)
    gme_end_date = sa.Column(sa.String, nullable=False)
    gme_status = sa.Column(sa.String, nullable=False)
    membership_status = sa.Column(sa.String, nullable=False)
    membership_product_code = sa.Column(sa.String, nullable=False)
    npi = sa.Column(sa.Integer, nullable=False)


class ResidencyProgramAddresses(Base):
    __tablename__ = 'residency_program_addresses'
    __table_args__ = {"schema": "oneview"}

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False)
    web_address = sa.Column(sa.String, nullable=False)
    old_name = sa.Column(sa.String, nullable=False)
    address_type = sa.Column(sa.String, nullable=False)
    address_one = sa.Column(sa.String, nullable=False)
    address_two = sa.Column(sa.String, nullable=False)
    address_three = sa.Column(sa.String, nullable=False)
    city = sa.Column(sa.String, nullable=False)
    state = sa.Column(sa.String, nullable=False)
    zipcode = sa.Column(sa.String, nullable=False)


class ResidencyProgramPersonnelMember(Base):
    __tablename__ = 'residency__program_personnel_member'
    __table_args__ = {"schema": "oneview"}

    id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    program_id = sa.Column(sa.Integer, sa.ForeignKey("oneview.residency_program_addresses.id"), nullable=False)
    personnel_type = sa.Column(sa.String, nullable=False)
    aamc_id = sa.Column(sa.Integer, nullable=False, unique=True)
    first_name = sa.Column(sa.String, nullable=False)
    middle_name = sa.Column(sa.String, nullable=False)
    last_name = sa.Column(sa.String, nullable=False)
    suffix_name = sa.Column(sa.String, nullable=False)
    degree_one = sa.Column(sa.String, nullable=False)
    degree_two = sa.Column(sa.String, nullable=False)
    degree_three = sa.Column(sa.String, nullable=False)
    phone_number = sa.Column(sa.String, nullable=False)
    email = sa.Column(sa.String, nullable=False)


class ResidencyProgramInstitution(Base):
    __tablename__ = 'residency_program_institution'
    __table_args__ = {"schema": "oneview"}

    id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    program_id = sa.Column(sa.Integer, sa.ForeignKey("oneview.residency_program_addresses.id"))


class Business(Base):
    __tablename__ = 'business'
    __table_args__ = {"schema": "oneview"}

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False)
    doing_business_as = sa.Column(sa.String, nullable=False)
    physical_address_one = sa.Column(sa.String, nullable=False)
    physical_address_two = sa.Column(sa.String, nullable=False)
    physical_city = sa.Column(sa.String, nullable=False)
    physical_state = sa.Column(sa.String, nullable=False)
    physical_zip_code = sa.Column(sa.String, nullable=False)
    postal_address_one = sa.Column(sa.String, nullable=False)
    postal_address_two = sa.Column(sa.String, nullable=False)
    postal_city = sa.Column(sa.String, nullable=False)
    postal_state = sa.Column(sa.String, nullable=False)
    postal_zip_code = sa.Column(sa.String, nullable=False)
    phone = sa.Column(sa.String, nullable=False)
    fax = sa.Column(sa.String, nullable=False)
    website = sa.Column(sa.String, nullable=False)
    owner_status = sa.Column(sa.String, nullable=False)
    profit_status = sa.Column(sa.String, nullable=False)


class Provider(Base):
    __tablename__ = 'provider'
    __table_args__ = {"schema": "oneview"}

    id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    # replace id with me number?
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
    primary_profession_code = sa.Column(sa.String, nullable=False)
    primary_profession_description = sa.Column(sa.String, nullable=False)
    status_description = sa.Column(sa.String, nullable=False)


class ProviderAffiliation(Base):
    __tablename__ = 'provider_affiliation'
    __table_args__ = {"schema": "oneview"}

    id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    business_id = sa.Column(sa.Integer, sa.ForeignKey("oneview.business.id"))
    provider_id = sa.Column(sa.Integer, sa.ForeignKey("oneview.provider.id"))
    description = sa.Column(sa.String, nullable=False)
    primary = sa.Column(sa.Boolean, default=False)
    rank = sa.Column(sa.String, nullable=False)


class CredentialingCustomer(Base):
    __tablename__ = 'credentialing_customer'
    __table_args__ = {"schema": "oneview"}

    id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    number = sa.Column(sa.String, nullable=False)
    isell_login = sa.Column(sa.String, nullable=False)
    name = sa.Column(sa.String, nullable=False)
    type = sa.Column(sa.String, nullable=False)
    type_description = sa.Column(sa.String, nullable=False)
    category = sa.Column(sa.String, nullable=False)
    category_description = sa.Column(sa.String, nullable=False)
    street_one = sa.Column(sa.String, nullable=False)
    street_two = sa.Column(sa.String, nullable=False)
    street_three = sa.Column(sa.String, nullable=False)
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
    customer_id = sa.Column(sa.Integer, sa.ForeignKey("oneview.credentialing_customer.id"), nullable=False)
    product_id = sa.Column(sa.Integer, sa.ForeignKey("oneview.credentialing_product.id"), nullable=False)
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
    ethnicity_id = sa.Column(sa.Integer, sa.ForeignKey("oneview.ethnicity.id"), nullable=False)


class Places(Base):
    __tablename__ = 'places'
    __table_args__ = {"schema": "oneview"}

    id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    customer_id = sa.Column(sa.Integer, sa.ForeignKey("oneview.credentialing_customer.id"), nullable=False)
    residency_program_institution_id = sa.Column(sa.Integer,
                                                 sa.ForeignKey("oneview.residency_program_institution.id"),
                                                 nullable=False)
    business_id = sa.Column(sa.Integer, sa.ForeignKey("oneview.business.id"), nullable=False)


class MedicalEducationPhysician(Base):
    __tablename__ = 'medical_education_physician'
    __table_args__ = {"schema": "oneview"}

    id = sa.Column(sa.Integer, sa.ForeignKey("oneview.residency__program_personnel_member.aamc_id"), primary_key=True,
                   nullable=False)
    medical_education_number = sa.Column(sa.Integer, sa.ForeignKey("oneview.physician.medical_education_number"),
                                         nullable=False)
