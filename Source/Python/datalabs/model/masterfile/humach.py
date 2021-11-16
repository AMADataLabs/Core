""" SQLAlchemy models for humach """
import sqlalchemy as sa
from   sqlalchemy.ext.declarative import declarative_base

from   datalabs.sqlalchemy import metadata

BASE = declarative_base(metadata=metadata())
SCHEMA = 'humach'

################################################################
# humach tables
################################################################

class Sample(BASE):
    __tablename__ = 'sample'
    __table_args__ = ({"schema": SCHEMA})

    sample_id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    row_id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    survey_month = sa.Column(sa.Integer, nullable=False)
    survey_year = sa.Column(sa.Integer, nullable=False)
    survey_type = sa.Column(sa.String, nullable=False)
    source = sa.Column(sa.String, nullable=False)
    me = sa.Column(sa.String, nullable=False)
    entity_id = sa.Column(sa.String)
    first_name = sa.Column(sa.String, nullable=False)
    middle_name = sa.Column(sa.String)
    last_name = sa.Column(sa.String, nullable=False)
    suffix = sa.Column(sa.String)
    address_comm_id = sa.Column(sa.String)
    address_line_0 = sa.Column(sa.String)
    address_line_1 = sa.Column(sa.String)
    address_line_2 = sa.Column(sa.String)
    city = sa.Column(sa.String)
    state = sa.Column(sa.String)
    zip = sa.Column(sa.String)
    phone_comm_id = sa.Column(sa.String)
    phone_number = sa.Column(sa.String, nullable=False)
    prim_spec_cd = sa.Column(sa.String)
    description = sa.Column(sa.String)
    pe_cd = sa.Column(sa.String)
    fax_number = sa.Column(sa.String)


class Results(BASE):
    __tablename__ = 'results'
    __table_args__ = ({"schema": SCHEMA})

    sample_id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    row_id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    study_cd = sa.Column(sa.String)
    me = sa.Column(sa.String, nullable=False)
    first_name = sa.Column(sa.String, nullable=False)
    middle_name = sa.Column(sa.String)
    last_name = sa.Column(sa.String, nullable=False)
    suffix = sa.Column(sa.String)
    degree = sa.Column(sa.String)
    label_name = sa.Column(sa.String)
    phone_number = sa.Column(sa.String, nullable=False)
    captured_phone_number = sa.Column(sa.String, nullable=False)
    correct_phone_number = sa.Column(sa.String)
    reason_phone_number_incorrect = sa.Column(sa.String)
    reason_phone_number_other = sa.Column(sa.String)
    address_line_0 = sa.Column(sa.String)
    address_line_1 = sa.Column(sa.String)
    address_line_2 = sa.Column(sa.String)
    city = sa.Column(sa.String)
    state = sa.Column(sa.String)
    zip = sa.Column(sa.String)
    captured_address_line_0 = sa.Column(sa.String)
    captured_address_line_1 = sa.Column(sa.String)
    captured_address_line_2 = sa.Column(sa.String)
    captured_city = sa.Column(sa.String)
    captured_state = sa.Column(sa.String)
    captured_zip = sa.Column(sa.String)
    correct_address = sa.Column(sa.String)
    reason_address_incorrect = sa.Column(sa.String)
    reason_address_other = sa.Column(sa.String)
    address_comment = sa.Column(sa.String)
    adcid = sa.Column(sa.String)
    secondattempt = sa.Column(sa.String)
    result_of_call = sa.Column(sa.String, nullable=False)
    result_filename = sa.Column(sa.String, nullable=False)
    result_date = sa.Column(sa.Date, nullable=False)
