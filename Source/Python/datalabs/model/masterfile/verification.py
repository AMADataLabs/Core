"""Masterfile verification data model"""
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base

from datalabs.sqlalchemy import metadata

Base = declarative_base(metadata=metadata())  # pylint: disable=invalid-name


class HumachSample(Base):
    __tablename__ = 'humach_sample'
    __table_args = (
        sa.PrimaryKeyConstraint('sample_id', 'row_id', name='pk_sample_rows')
    )
    sample_id = sa.Column(sa.Integer, nullable=False)
    row_id = sa.Column(sa.Integer, nullable=False)
    survey_month = sa.Column(sa.Integer, nullable=False)
    survey_year = sa.Column(sa.Integer, nullable=False)
    survey_type = sa.Column(sa.String, nullable=False)
    sample_source = sa.Column(sa.String, nullable=False)
    me = sa.Column(sa.String(length=11), nullable=False)
    entity_id = sa.Column(sa.String, nullable=False)
    first_name = sa.Column(sa.String, nullable=False)
    middle_name = sa.Column(sa.String, nullable=False)
    last_name = sa.Column(sa.String, nullable=False)
    suffix = sa.Column(sa.String, nullable=False)
    polo_comm_id = sa.Column(sa.String, nullable=False)
    polo_mailing_line_1 = sa.Column(sa.String, nullable=False)
    polo_mailing_line_2 = sa.Column(sa.String, nullable=False)
    polo_city = sa.Column(sa.String, nullable=False)
    polo_state = sa.Column(sa.String, nullable=False)
    polo_zip = sa.Column(sa.String, nullable=False)
    phone_comm_id = sa.Column(sa.String, nullable=False)
    telephone_number = sa.Column(sa.String, nullable=False)
    prim_spec_cd = sa.Column(sa.String, nullable=False)
    description = sa.Column(sa.String, nullable=False)
    pe_cd = sa.Column(sa.String, nullable=False)
    fax_number = sa.Column(sa.String, nullable=False)


class HumachResult(Base):
    __tablename__ = 'humach_result'
    __table_args = (
        sa.PrimaryKeyConstraint('sample_id', 'row_id', name='pk_sample_rows')
    )
    sample_id = sa.Column(sa.Integer, nullable=False)
    row_id = sa.Column(sa.Integer, nullable=False)
    physician_me_number = sa.Column(sa.String(length=11), nullable=False)
    physician_first_name = sa.Column(sa.String, nullable=True)
    physician_middle_name = sa.Column(sa.String, nullable=True)
    physician_last_name = sa.Column(sa.String, nullable=True)
    suffix = sa.Column(sa.String, nullable=True)
    degree = sa.Column(sa.String, nullable=True)
    office_address_line_1 = sa.Column(sa.String, nullable=True)
    office_address_line_2 = sa.Column(sa.String, nullable=True)
    office_address_city = sa.Column(sa.String, nullable=True)
    office_address_state = sa.Column(sa.String, nullable=True)
    office_address_zip = sa.Column(sa.String, nullable=True)
    office_address_verified_updated = sa.Column(sa.String, nullable=True)
    office_telephone = sa.Column(sa.String, nullable=True)
    office_phone_verified_updated = sa.Column(sa.String, nullable=True)
    office_fax = sa.Column(sa.String, nullable=True)
    office_fax_verified_updated = sa.Column(sa.String, nullable=True)
    specialty = sa.Column(sa.String, nullable=True)
    specialty_updated = sa.Column(sa.String, nullable=True)
    present_employment_code = sa.Column(sa.String, nullable=True)
    present_employment_updated = sa.Column(sa.String, nullable=True)
    comments = sa.Column(sa.String, nullable=True)
    source = sa.Column(sa.String, nullable=True)
    source_date = sa.Column(sa.Date, nullable=True)


class SampleReference(Base):
    __tablename__ = 'sample_reference'
    __table_args__ = (
        sa.PrimaryKeyConstraint('humach_sample_id', 'other_sample_id', name='pk_sample_id')
    )

    humach_sample_id = sa.Column(sa.Integer, sa.ForeignKey('humach_sample.sample_id'))
    other_sample_id = sa.Column(sa.Integer, nullable=False)
    other_sample_source = sa.Column(sa.String, nullable=False)
