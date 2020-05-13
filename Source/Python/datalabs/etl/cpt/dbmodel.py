""" SQLAlchemy models for CPT """
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base

naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = sa.MetaData(naming_convention=naming_convention)

Base = declarative_base(metadata=metadata)


class Description(Base):
    __tablename__ = 'description'
    __table_args__ = {"schema": "cpt"}

    cpt_code = sa.Column(sa.String(5), primary_key=True)
    short = sa.Column(sa.String(28), nullable=False)
    medium = sa.Column(sa.String(48), nullable=False)
    long = sa.Column(sa.String(), nullable=False)
    data_created = sa.Column(sa.String(), nullable=False)
    data_modified = sa.Column(sa.String(), nullable=False)


class Descriptor(Base):
    __tablename__ = 'descriptor'
    __table_args__ = {"schema": "cpt"}

    id = sa.Column(sa.Integer, primary_key=True)
    cpt_code = sa.Column(sa.String(5), sa.ForeignKey("cpt.description.cpt_code"), nullable=False)
    concept_id = sa.Column(sa.Integer, nullable=False)
    clinician = sa.Column(sa.String, nullable=False)
    consumer = sa.Column(sa.String, nullable=False)
    data_created = sa.Column(sa.String(), nullable=False)
    data_modified = sa.Column(sa.String(), nullable=False)


class ModifierType(Base):
    __tablename__ = 'modifier_type'
    __table_args__ = {"schema": "cpt"}

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(20), nullable=False)


class Modifier(Base):
    __tablename__ = 'modifier'
    __table_args__ = {"schema": "cpt"}

    mod_code = sa.Column(sa.String(2), primary_key=True)
    type_id = sa.Column(sa.Integer, sa.ForeignKey("cpt.modifier_type.id"), nullable=False)
    description = sa.Column(sa.String, nullable=False)
    data_created = sa.Column(sa.String(), nullable=False)
    data_modified = sa.Column(sa.String(), nullable=False)
