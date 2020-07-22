""" SQLAlchemy models for CPT """
import sqlalchemy as sa
from   sqlalchemy.ext.declarative import declarative_base

from   datalabs.sqlalchemy import metadata

Base = declarative_base(metadata=metadata())  # pylint: disable=invalid-name


# === CPT Standard Tables ===
class ReleaseType(Base):
    __tablename__ = 'release_type'
    __table_args__ = {"schema": "cpt"}

    type = sa.Column(sa.String(6), primary_key=True)  # ANNUAL, PLA-Q1, PLA-Q2, PLA-Q3, PLA-Q4, OTHER
    publish_month = sa.Column(sa.String(3), nullable=False)
    publish_day = sa.Column(sa.Integer, nullable=False)
    effective_month = sa.Column(sa.String(3), nullable=False)
    effective_day = sa.Column(sa.Integer, nullable=False)


class Release(Base):
    __tablename__ = 'release'
    __table_args__ = {"schema": "cpt"}

    id = sa.Column(sa.Integer, primary_key=True)
    publish_date = sa.Column(sa.Date, nullable=False)
    effective_date = sa.Column(sa.Date, nullable=False)
    type = sa.Column(sa.String(6), sa.ForeignKey("cpt.release_type.type"), nullable=False)


class Code(Base):
    __tablename__ = 'code'
    __table_args__ = {"schema": "cpt"}

    code = sa.Column(sa.String(5), primary_key=True)
    modified_date = sa.Column(sa.Date, nullable=False)
    deleted = sa.Column(sa.Boolean, nullable=False, default=False)


class ReleaseCodeMapping(Base):
    __tablename__ = 'release_code_mapping'
    __table_args__ = {"schema": "cpt"}

    id = sa.Column(sa.Integer, primary_key=True)
    release = sa.Column(sa.Integer, sa.ForeignKey("cpt.release.id"), nullable=True)
    code = sa.Column(sa.String(5), sa.ForeignKey("cpt.code.code"), nullable=False)


class ShortDescriptor(Base):
    __tablename__ = 'short_descriptor'
    __table_args__ = {"schema": "cpt"}

    code = sa.Column(sa.String(5), sa.ForeignKey("cpt.code.code"), primary_key=True)
    descriptor = sa.Column(sa.String(28), nullable=False)
    modified_date = sa.Column(sa.Date, nullable=False)
    deleted = sa.Column(sa.Boolean, nullable=False, default=False)


class MediumDescriptor(Base):
    __tablename__ = 'medium_descriptor'
    __table_args__ = {"schema": "cpt"}

    code = sa.Column(sa.String(5), sa.ForeignKey("cpt.code.code"), primary_key=True)
    descriptor = sa.Column(sa.String(48), nullable=False)
    modified_date = sa.Column(sa.Date, nullable=False)
    deleted = sa.Column(sa.Boolean, nullable=False, default=False)


class LongDescriptor(Base):
    __tablename__ = 'long_descriptor'
    __table_args__ = {"schema": "cpt"}

    code = sa.Column(sa.String(5), sa.ForeignKey("cpt.code.code"), primary_key=True)
    descriptor = sa.Column(sa.String(), nullable=False)
    modified_date = sa.Column(sa.Date, nullable=False)
    deleted = sa.Column(sa.Boolean, nullable=False, default=False)


class ConsumerDescriptor(Base):
    __tablename__ = 'consumer_descriptor'
    __table_args__ = {"schema": "cpt"}

    code = sa.Column(sa.String(5), sa.ForeignKey("cpt.code.code"), primary_key=True)
    descriptor = sa.Column(sa.String, nullable=False)
    modified_date = sa.Column(sa.Date, nullable=False)
    deleted = sa.Column(sa.Boolean, nullable=False, default=False)


class ClinicianDescriptor(Base):
    __tablename__ = 'clinician_descriptor'
    __table_args__ = {"schema": "cpt"}

    id = sa.Column(sa.Integer, primary_key=True)
    descriptor = sa.Column(sa.String, nullable=False)
    modified_date = sa.Column(sa.Date, nullable=False)
    deleted = sa.Column(sa.Boolean, nullable=False, default=False)


class ClinicianDescriptorCodeMapping(Base):
    __tablename__ = 'clinician_descriptor_code_mapping'
    __table_args__ = {"schema": "cpt"}

    clinician_descriptor = sa.Column(sa.Integer, sa.ForeignKey("cpt.clinician_descriptor.id"), primary_key=True)
    code = sa.Column(sa.String(5), sa.ForeignKey("cpt.code.code"), nullable=False)


class ModifierType(Base):
    __tablename__ = 'modifier_type'
    __table_args__ = {"schema": "cpt"}

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(30), nullable=False)


class Modifier(Base):
    __tablename__ = 'modifier'
    __table_args__ = {"schema": "cpt"}

    modifier = sa.Column(sa.String(2), primary_key=True)
    type = sa.Column(sa.Integer, sa.ForeignKey("cpt.modifier_type.id"), nullable=False)
    descriptor = sa.Column(sa.String, nullable=False)
    modified_date = sa.Column(sa.Date, nullable=False)
    deleted = sa.Column(sa.Boolean, nullable=False, default=False)


# === CPT Link Tables ===
class Concept(Base):
    __tablename__ = 'concept'
    __table_args__ = {"schema": "cpt"}

    id = sa.Column(sa.Integer, primary_key=True)
    cpt_code = sa.Column(sa.String(5), sa.ForeignKey("cpt.code.code"), nullable=False)
    modified_date = sa.Column(sa.Date, nullable=False)
    deleted = sa.Column(sa.Boolean, nullable=False, default=False)


class PLADetails(Base):
    __tablename__ = 'pla_code'
    __table_args__ = {"schema": "cpt"}

    code = sa.Column(sa.String(5), nullable=False, primary_key=True)
    status = sa.Column(sa.String, nullable=False)
    test_name = sa.Column(sa.String, nullable=False)
    modified_date = sa.Column(sa.Date, nullable=False)


class Manufacturer(Base):
    __tablename__ = 'manufacturer'
    __table_args__ = {"schema": "cpt"}

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False)
    modified_date = sa.Column(sa.Date, nullable=False)
    deleted = sa.Column(sa.Boolean, nullable=False, default=False)


class ManufacturerPLACodeMapping(Base):
    __tablename__ = 'manufacturer_pla_code_mapping'
    __table_args__ = {"schema": "cpt"}

    code = sa.Column(sa.String(5), sa.ForeignKey("cpt.pla_code.code"), primary_key=True)
    manufacturer = sa.Column(sa.Integer, sa.ForeignKey("cpt.manufacturer.id"), nullable=False)


class Lab(Base):
    __tablename__ = 'lab'
    __table_args__ = {"schema": "cpt"}

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False)
    modified_date = sa.Column(sa.Date, nullable=False)
    deleted = sa.Column(sa.Boolean, nullable=False, default=False)


class LabPLACodeMapping(Base):
    __tablename__ = 'lab_pla_code_mapping'
    __table_args__ = {"schema": "cpt"}

    code = sa.Column(sa.String(5), sa.ForeignKey("cpt.pla_code.code"), primary_key=True)
    lab = sa.Column(sa.Integer, sa.ForeignKey("cpt.lab.id"), nullable=False)




class ReleasePLACodeMapping(Base):
    __tablename__ = 'release_pla_code_mapping'
    __table_args__ = {"schema": "cpt"}

    id = sa.Column(sa.Integer, primary_key=True)
    release = sa.Column(sa.Integer, sa.ForeignKey("cpt.release.id"), nullable=True)
    code = sa.Column(sa.String(5), sa.ForeignKey("cpt.pla_code.code"), nullable=False)
