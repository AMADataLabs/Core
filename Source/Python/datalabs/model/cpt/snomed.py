""" SQLAlchemy models for CPT """
import sqlalchemy as sa

from   datalabs.model.dynamodb import Base

class Mapping(Base):
    __abstract__ = True
    __tablename__ = "CPT-API-snomed"

    sk = sa.Column(sa.String, primary_key=True)
    pk = sa.Column(sa.String, nullable=False)
    snomed_descriptor = sa.Column(sa.String, nullable=False)
    map_category = sa.Column(sa.String, nullable=False)
    cpt_descriptor = sa.Column(sa.Integer, nullable=False)


class Keyword(Base):
    __abstract__ = True
    __tablename__ = "CPT-API-snomed"

    sk = sa.Column(sa.String, primary_key=True)
    pk = sa.Column(sa.String, nullable=False)

