""" SQLAlchemy models for OneView """
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base

from datalabs.sqlalchemy import metadata

Base = declarative_base(metadata=metadata())  # pylint: disable=invalid-name


class PPD(Base):
    __tablename__ = 'ppd'
    __table_args__ = {"schema": "cpt"}

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
    address_city = sa.Column(sa.String, nullable=False)
    address_state = sa.Column(sa.String, nullable=False)
    address_zip = sa.Column(sa.String, nullable=False)
    address_zip_plus_4 = sa.Column(sa.String, nullable=False)
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
    npi_number = sa.Column(sa.String, nullable=False)
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


class ProgramInformation(Base):
    __tablename__ = 'program_information'
    __table_args__ = {"schema": "meri"}

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False)
    web_address = sa.Column(sa.String, nullable=False)
    old_name = sa.Column(sa.String, nullable=False)


class ProgramAddresses(Base):
    __tablename__ = 'program_addresses'
    __table_args__ = {"schema": "meri"}

    id = sa.Column(sa.Integer, sa.ForeignKey("program_information.id"), primary_key=True, nullable=False)
    address_type = sa.Column(sa.String, nullable=False)
    address_one = sa.Column(sa.String, nullable=False)
    address_two = sa.Column(sa.String, nullable=False)
    address_three = sa.Column(sa.String, nullable=False)
    city = sa.Column(sa.String, nullable=False)
    state = sa.Column(sa.String, nullable=False)
    zip_code = sa.Column(sa.String, nullable=False)


class ProgramPersonnel(Base):
    __tablename__ = 'program_personnel'
    __table_args__ = {"schema": "meri"}

    id = sa.Column(sa.Integer, sa.ForeignKey("program_information.id"), primary_key=True)
    personnel_type = sa.Column(sa.String, nullable=False)
    aamc_id = sa.Column(sa.String, nullable=False)
    first_name = sa.Column(sa.String, nullable=False)
    middle_name = sa.Column(sa.String, nullable=False)
    last_name = sa.Column(sa.String, nullable=False)
    suffix_name = sa.Column(sa.String, nullable=False)
    degree_one = sa.Column(sa.String, nullable=False)
    degree_two = sa.Column(sa.String, nullable=False)
    degree_three = sa.Column(sa.String, nullable=False)
    phone_number = sa.Column(sa.String, nullable=False)
    email = sa.Column(sa.String, nullable=False)


class InstitutionInformation(Base):
    __tablename__ = 'institution_information'
    __table_args__ = {"schema": "meri"}

    program_id = sa.Column(sa.Integer, sa.ForeignKey("program_information.id"), )
    institution_id = sa.Column(sa.Integer, primary_key=True)


class Business(Base):
    __tablename__ = 'business'
    __table_args__ = {"schema": "IQVia"}

    ims_org_id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False)
    dba = sa.Column(sa.String, nullable=False)
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


class Professional(Base):
    __tablename__ = 'professional'
    __table_args__ = {"schema": "IQVia"}

    id = sa.Column(sa.Integer, primary_key=True)
    first_name = sa.Column(sa.String, nullable=False)
    middle_name = sa.Column(sa.String, nullable=False)
    last_name = sa.Column(sa.String, nullable=False)
    gen_suffix = sa.Column(sa.String, nullable=False)
    designation = sa.Column(sa.String, nullable=False)
    gender = sa.Column(sa.String, nullable=False)
    role = sa.Column(sa.String, nullable=False)
    primary_specialty = sa.Column(sa.String, nullable=False)
    secondary_specialty = sa.Column(sa.String, nullable=False)
    tertiary_specialty = sa.Column(sa.String, nullable=False)
    primary_code = sa.Column(sa.String, nullable=False)
    primary_description = sa.Column(sa.String, nullable=False)
    medical_education_number = sa.Column(sa.Integer, sa.ForeignKey("ppd.medical_education_number"), nullable=False)
    status_description = sa.Column(sa.String, nullable=False)


class ProviderAffiliationFact(Base):
    __tablename__ = 'provider_affiliation_fact'
    __table_args__ = {"schema": "IQVia"}

    ims_org_id = sa.Column(sa.Integer, sa.ForeignKey("professional.id"), primary_key=True)
    type_id = sa.Column(sa.String, nullable=False)
    # what is ind?
    ind = sa.Column(sa.String, nullable=False)
    rank = sa.Column(sa.String, nullable=False)
    professional_id = sa.Column(sa.String, nullable=False)


class AffiliationType(Base):
    __tablename__ = 'affiliation_type'
    __table_args__ = {"schema": "IQVia"}

    type_id = sa.Column(sa.Integer, primary_key=True)
    type_description = sa.Column(sa.String, nullable=False)


class DIMCustomer(Base):
    __tablename__ = 'dim_customer'
    __table_args__ = {"schema": "Credentialing"}

    key = sa.Column(sa.Integer, primary_key=True)
    number = sa.Column(sa.String, nullable=False)
    isell_login = sa.Column(sa.String, nullable=False)
    name = sa.Column(sa.String, nullable=False)
    type = sa.Column(sa.String, nullable=False)
    type_description = sa.Column(sa.String, nullable=False)
    category = sa.Column(sa.String, nullable=False)
    category_description = sa.Column(sa.String, nullable=False)


class FactEprofileOrders(Base):
    __tablename__ = 'fact_eprofile_orders'
    __table_args__ = {"schema": "Credentialing"}

    key = sa.Column(sa.Integer, sa.ForeignKey("dim_customer.key"), primary_key=True)
    dt_key = sa.Column(sa.String, nullable=False)
    number = sa.Column(sa.String, nullable=False)
    product_id = sa.Column(sa.String, nullable=False)
    physician_history_key = sa.Column(sa.String, nullable=False)


class DIMPhysicianHistory(Base):
    __tablename__ = 'dim_physician_history'
    __table_args__ = {"schema": "Credentialing"}

    key = sa.Column(sa.Integer, sa.ForeignKey("fact_eprofile_orders.physician_history_key"), primary_key=True)
    medical_education_number = sa.Column(sa.String, nullable=False)


class DIMDate(Base):
    __tablename__ = 'dim_date'
    __table_args__ = {"schema": "Credentialing"}

    key = sa.Column(sa.Integer, primary_key=True)
    full_dt = sa.Column(sa.String, nullable=False)


class DIMProduct(Base):
    __tablename__ = 'dim_product'
    __table_args__ = {"schema": "Credentialing"}

    product_id = sa.Column(sa.Integer, primary_key=True)
    product_description = sa.Column(sa.String, nullable=False)


class OrganizationAddresses(Base):
    __tablename__ = 'organization_addresses'
    __table_args__ = {"schema": "Credentialing"}

    id = sa.Column(sa.Integer, primary_key=True)
    customer_number = sa.Column(sa.String, nullable=False)
    company_name = sa.Column(sa.String, nullable=False)
    street_first = sa.Column(sa.String, nullable=False)
    street_second = sa.Column(sa.String, nullable=False)
    street_third = sa.Column(sa.String, nullable=False)
    city = sa.Column(sa.String, nullable=False)
    state = sa.Column(sa.String, nullable=False)
    zipcode = sa.Column(sa.String, nullable=False)
    phone_number = sa.Column(sa.String, nullable=False)


class EthnicityAims(Base):
    __tablename__ = 'ethnicity_aims'
    __table_args__ = {"schema": "Race-Ethnicity"}

    medical_education_number = sa.Column(sa.String, sa.ForeignKey("ppd.medical_education_number"), primary_key=True)
    identity_detail_cd = sa.Column(sa.String, nullable=False)


class AAMCCodeValues(Base):
    __tablename__ = 'aamc_code_values'
    __table_args__ = {"schema": "Race-Ethnicity"}

    identity_detail_cd = sa.Column(sa.String, sa.ForeignKey("ethnicity_aims.identity_detail_cd"), primary_key=True)
    identity_description = sa.Column(sa.String, nullable=False)
