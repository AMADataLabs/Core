""" SQLAlchemy models for CPT """
import sqlalchemy as sa
from   sqlalchemy.ext.declarative import declarative_base

from   datalabs.sqlalchemy import metadata

Base = declarative_base(metadata=metadata())  # pylint: disable=invalid-name

SCHEMA = 'marketing'


class Contact(Base):
    __tablename__ = 'contact'
    __table_args__ = {"schema": SCHEMA}

    email = sa.Column(sa.String, primary_key=True)
    hs_contact_id = sa.Column(sa.String(length=15), nullable=False)
    email_last_validated = sa.Column(sa.Date)
