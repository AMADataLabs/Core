# pylint: disable=invalid-name
""" Snowflake SQLAlchemy models for CPT """
import sqlalchemy as sa
from   sqlalchemy.ext.declarative import declarative_base

from   datalabs.sqlalchemy import metadata

BASE = declarative_base(metadata=metadata())

class CustomerBusiness(BASE):
    __tablename__ = 'customer_business'
    __table_args__ = {"schema": "oneview"}

    customer = sa.Column(sa.Integer, nullable=False, primary_key=True)
    business = sa.Column(sa.Integer, nullable=False)
