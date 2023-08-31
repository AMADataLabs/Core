""" SQLAlchemy models for CPT """
import sqlalchemy as sa
from   sqlalchemy.ext.declarative import declarative_base

from   datalabs.sqlalchemy import metadata

Base = declarative_base(metadata=metadata())  # pylint: disable=invalid-name


# === Platform Licensing Tables ===
class Organization(Base):
    __tablename__ = 'organizations'

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False)


class Article(Base):
    __tablename__ = 'articles'

    id = sa.Column(sa.Integer, primary_key=True)
    article_name = sa.Column(sa.String, nullable=False)


class TrafficCounts(Base):
    __tablename__ = 'TrafficCounts'

    id = sa.Column(sa.Integer, primary_key=True)
    applicants_signed_in = sa.Column(sa.Integer, nullable=False)
    applications_started = sa.Column(sa.Integer, nullable=False)
    applications_saved = sa.Column(sa.Integer, nullable=False)
    applications_completed_sent_to_portal = sa.Column(sa.Integer, nullable=False)
    applications_completed_exempt = sa.Column(sa.Integer, nullable=False)
    applicants_international = sa.Column(sa.Integer, nullable=False)
    applicants_distribution = sa.Column(sa.Integer, nullable=False)
    lab_applications_pre_tax_flagged = sa.Column(sa.Integer, nullable=False)
    lab_applications_post_tax_flagged = sa.Column(sa.Integer, nullable=False)
    individual_users_under_26_flagged = sa.Column(sa.Integer, nullable=False)
    other_flagged_applications = sa.Column(sa.Integer, nullable=False)
    data_collection_date = sa.Column(sa.String, nullable=False)


class Groups(Base):
    __tablename__ = 'Groups'

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False)
    organization_id = sa.Column(sa.Integer, nullable=False)
    client_id = sa.Column(sa.String, nullable=False)
    secret = sa.Column(sa.String, nullable=False)
    environment_id = sa.Column(sa.Integer, nullable=False)
    resource_id = sa.Column(sa.Integer, nullable=False)
    valid_from = sa.Column(sa.String, nullable=False)
    valid_to = sa.Column(sa.String, nullable=False)
    renewal_reminders = sa.Column(sa.Integer, nullable=False)
    quote_id = sa.Column(sa.Integer, nullable=False)
