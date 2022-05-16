""" SQLAlchemy models for CPT """
import sqlalchemy as sa
from   sqlalchemy.ext.declarative import declarative_base

from   datalabs.sqlalchemy import metadata

Base = declarative_base(metadata=metadata())  # pylint: disable=invalid-name


# === Frinctionless Licensing Tables ===
class Organization(Base):
    __tablename__ = 'organizations'

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False)
    account_exec = sa.Column(sa.String, nullable=False)
    cad = sa.Column(sa.String, nullable=False)
    contract_type = sa.Column(sa.String, nullable=False)
    contract_status = sa.Column(sa.String, nullable=False)
    status_last_updated_date = sa.Column(sa.String, nullable=False)
    effective_date = sa.Column(sa.String, nullable=False)
    start_date = sa.Column(sa.String, nullable=False)
    expiration_date = sa.Column(sa.String, nullable=False)
    properties = sa.Column(sa.String, nullable=False)
    articles = sa.Column(sa.String, nullable=False)
    territories = sa.Column(sa.String, nullable=False)
    channels = sa.Column(sa.String, nullable=False)
    street = sa.Column(sa.String, nullable=False)
    city = sa.Column(sa.String, nullable=False)
    state = sa.Column(sa.String, nullable=False)
    zip_code = sa.Column(sa.String, nullable=False)
    website = sa.Column(sa.String, nullable=False)
    agreement_version_number = sa.Column(sa.String, nullable=False)
    zendesk_ticket_id = sa.Column(sa.String, nullable=False)
    source = sa.Column(sa.String, nullable=False)

