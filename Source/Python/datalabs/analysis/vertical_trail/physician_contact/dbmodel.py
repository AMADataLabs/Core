import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base

from datalabs.sqlalchemy import metadata

Base = declarative_base(metadata=metadata())  # pylint: disable=invalid-name


class VerticalTrailSample(Base):
    __tablename__ = 'vertical_trail_samples'
    __table_args__ = {'schema': 'operations_archive'}

    sample_id = sa.Column(sa.Integer, nullable=False)
    row_id = sa.Column(sa.Integer, nullable=False)
    sample_date = sa.Column(sa.Date, nullable=False)
    me = sa.Column(sa.String(11), nullable=False)
    last_name = sa.Column(sa.String, nullable=False)
    first_name = sa.Column(sa.String, nullable=False)
    middle_name = sa.Column(sa.String, nullable=True)
    medschool_grad_year = sa.Column(sa.String, nullable=True)
    medschool_name = sa.Column(sa.String, nullable=True)
    degree_type = sa.Column(sa.String, nullable=True)
    specialty = sa.Column(sa.String, nullable=True)
    polo_city = sa.Column(sa.String, nullable=True)
    polo_state = sa.Column(sa.String, nullable=True)
    polo_zip = sa.Column(sa.String, nullable=True)
    lic_state = sa.Column(sa.String, nullable=True)
    lic_nbr = sa.Column(sa.String, nullable=True)
    oldphone1 = sa.Column(sa.String, nullable=True)
    oldphone2 = sa.Column(sa.String, nullable=True)
    oldphone3 = sa.Column(sa.String, nullable=True)
    oldphone4 = sa.Column(sa.String, nullable=True)
    oldphone5 = sa.Column(sa.String, nullable=True)
    oldphone6 = sa.Column(sa.String, nullable=True)
    oldphone7 = sa.Column(sa.String, nullable=True)
    oldphone8 = sa.Column(sa.String, nullable=True)
    oldphone9 = sa.Column(sa.String, nullable=True)
    oldphone10 = sa.Column(sa.String, nullable=True)
    oldphone11 = sa.Column(sa.String, nullable=True)
    oldphone12 = sa.Column(sa.String, nullable=True)
    oldphone13 = sa.Column(sa.String, nullable=True)

    sa.UniqueConstraint('sample_id', 'row_id')


class VerticalTrailResult(Base):
    __tablename__ = 'vertical_trail_results'
    __table_args__ = {'schema': 'operations_archive'}

    sample_id = sa.Column(sa.Integer, sa.ForeignKey("operations_archive.vertical_trail_samples.sample_id"))
    row_id = sa.Column(sa.Integer, nullable=False)
    sample_date = sa.Column(sa.Date, nullable=False)
    phone_number = sa.Column(sa.String, nullable=True)
    fax_number = sa.Column(sa.String, nullable=True)
    email = sa.Column(sa.String, nullable=True)
    notes = sa.Column(sa.String, nullable=True)

    sa.UniqueConstraint('sample_id', 'row_id')

