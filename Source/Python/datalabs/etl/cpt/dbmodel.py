""" SQLAlchemy models for CPT """
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base

from datalabs.sqlalchemy import metadata


Base = declarative_base(metadata=metadata())  # pylint: disable=invalid-name


# === CPT Standard Tables ===
class ReleaseType(Base):
    __tablename__ = 'release_type'
    __table_args__ = {"schema": "cpt"}

    type = sa.Column(sa.String(3), primary_key=True)  # Y, Q1, Q2, Q3, Q4


class Release(Base):
    __tablename__ = 'release'
    __table_args__ = {"schema": "cpt"}

    id = sa.Column(sa.Integer, primary_key=True)
    date = sa.Column(sa.Date, nullable=False)
    type = sa.Column(sa.String(3), sa.ForeignKey("cpt.release_type.type"), nullable=False)


class Code(Base):
    __tablename__ = 'code'
    __table_args__ = {"schema": "cpt"}

    code = sa.Column(sa.String(5), primary_key=True)


class ReleaseCodeMapping(Base):
    __tablename__ = 'release_code_mapping'
    __table_args__ = {"schema": "cpt"}

    release = sa.Column(sa.Integer, sa.ForeignKey("cpt.release.id"), primary_key=True)
    code = sa.Column(sa.String(5), sa.ForeignKey("cpt.code.code"), nullable=False)


class ShortDescriptor(Base):
    __tablename__ = 'short_descriptor'
    __table_args__ = {"schema": "cpt"}

    code = sa.Column(sa.String(5), sa.ForeignKey("cpt.code.code"), primary_key=True)
    descriptor = sa.Column(sa.String(28), nullable=False)


class MediumDescriptor(Base):
    __tablename__ = 'medium_descriptor'
    __table_args__ = {"schema": "cpt"}

    code = sa.Column(sa.String(5), sa.ForeignKey("cpt.code.code"), primary_key=True)
    descriptor = sa.Column(sa.String(48), nullable=False)


class LongDescriptor(Base):
    __tablename__ = 'long_descriptor'
    __table_args__ = {"schema": "cpt"}

    code = sa.Column(sa.String(5), sa.ForeignKey("cpt.code.code"), primary_key=True)
    descriptor = sa.Column(sa.String(), nullable=False)


class ConsumerDescriptor(Base):
    __tablename__ = 'consumer_descriptor'
    __table_args__ = {"schema": "cpt"}

    code = sa.Column(sa.String(5), sa.ForeignKey("cpt.code.code"), primary_key=True)
    descriptor = sa.Column(sa.String, nullable=False)


class ClinicianDescriptor(Base):
    __tablename__ = 'clinician_descriptor'
    __table_args__ = {"schema": "cpt"}

    id = sa.Column(sa.Integer, primary_key=True)
    descriptor = sa.Column(sa.String, nullable=False)


class ClinicianDescriptorCodeMapping(Base):
    __tablename__ = 'clinician_descriptor_code_mapping'
    __table_args__ = {"schema": "cpt"}

    clinician_descriptor = sa.Column(sa.Integer, sa.ForeignKey("cpt.clinician_descriptor.id"), primary_key=True)
    code = sa.Column(sa.String(5), sa.ForeignKey("cpt.code.code"), nullable=False)


class ModifierType(Base):
    __tablename__ = 'modifier_type'
    __table_args__ = {"schema": "cpt"}

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(20), nullable=False)


class Modifier(Base):
    __tablename__ = 'modifier'
    __table_args__ = {"schema": "cpt"}

    modifier = sa.Column(sa.String(2), primary_key=True)
    type = sa.Column(sa.Integer, sa.ForeignKey("cpt.modifier_type.id"), nullable=False)
    descriptor = sa.Column(sa.String, nullable=False)


# === CPT Link Tables ===
class Concept(Base):
    __tablename__ = 'concept'
    __table_args__ = {"schema": "cpt"}

    id = sa.Column(sa.Integer, primary_key=True)
    cpt_code = sa.Column(sa.String(5), sa.ForeignKey("cpt.code.code"), nullable=False)
