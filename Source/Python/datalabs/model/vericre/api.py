""" SQLAlchemy models for VeriCre """
import uuid

import sqlalchemy as sa
from   sqlalchemy.dialects.postgresql import UUID, JSONB
from   sqlalchemy.ext.declarative import declarative_base

from   datalabs.sqlalchemy import metadata

BASE = declarative_base(metadata=metadata())
SCHEMA = 'public'


class CommonColumns:
    created_at = sa.Column(sa.BigInteger) # , nullable=True
    created_by = sa.Column(UUID(as_uuid=True))
    is_deleted = sa.Column(sa.Boolean)
    updated_at = sa.Column(sa.BigInteger)
    updated_by = sa.Column(UUID(as_uuid=True))


class Institution(BASE):
    __tablename__ = 'institution'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.BigInteger, primary_key=True, nullable=False)
    name = sa.Column(sa.String(255))
    cms_certificate = sa.Column(sa.String(255))
    logo = sa.Column(sa.String(255))
    abbreviation = sa.Column(sa.String(255))


class InstitutionManagement(BASE, CommonColumns):
    __tablename__ = 'institution_management'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.BigInteger, sa.Sequence('inst_mgmt_seq', start=1, increment=1), primary_key=True, nullable=False)
    status = sa.Column(sa.String(255))
    institution = sa.Column(sa.BigInteger)


class User(BASE, CommonColumns):
    __tablename__ = 'user'
    __table_args__ = (
        sa.Index('user_ama_entity_id_idx', 'ama_entity_id'),
        sa.Index('user_ama_me_number_idx', 'ama_me_number'),
        {"schema": SCHEMA}
    )

    id = sa.Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    avatar_image = sa.Column(sa.String(255))
    avatar_image_expire_time = sa.Column(sa.BigInteger)
    avatar_image_url = sa.Column(sa.Text)
    email_id = sa.Column(sa.String(255), nullable=False)
    first_name = sa.Column(sa.String(255))
    last_name = sa.Column(sa.String(255))
    role = sa.Column(sa.String(255))
    sso_id = sa.Column(sa.String(255))
    status = sa.Column(sa.String(255))
    institution = sa.Column(sa.BigInteger)
    ama_me_number = sa.Column(sa.String(255))
    ama_name = sa.Column(sa.String(255))
    ama_user_name = sa.Column(sa.String(255))
    preferences = sa.Column(JSONB)
    is_consented = sa.Column(sa.Boolean)
    ama_entity_id = sa.Column(sa.String(255))


class Form(BASE):
    __tablename__ = 'form'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.BigInteger, sa.Sequence('form_seq', start=1, increment=1), primary_key=True, nullable=False)
    is_main_form = sa.Column(sa.Boolean)
    name = sa.Column(sa.String(512))
    status = sa.Column(sa.String(255))


class FormField(BASE):
    __tablename__ = 'form_field'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.BigInteger, sa.Sequence('form_field_seq', start=1, increment=1), primary_key=True, nullable=False)
    name = sa.Column(sa.String(512))
    identifier = sa.Column(sa.String(255))
    type = sa.Column(sa.String(255))
    size = sa.Column(sa.String(255))
    is_hidden = sa.Column(sa.Boolean)
    read_only = sa.Column(sa.Boolean)
    order = sa.Column(sa.BigInteger)
    alias = sa.Column(sa.String(255))
    alternate_name = sa.Column(sa.String(255))
    is_source_field = sa.Column(sa.Boolean)
    source_tag = sa.Column(sa.String(255))
    is_authoritative = sa.Column(sa.Boolean)
    source_key = sa.Column(sa.String(255))
    source = sa.Column(sa.BigInteger)
    option = sa.Column(sa.BigInteger)
    parent_field_id = sa.Column(sa.String(255))
    values = sa.Column(JSONB)
    is_verified = sa.Column(sa.Boolean)
    placeholder = sa.Column(sa.String(255))
    form_sub_section = sa.Column(sa.BigInteger)
    form_adddendum_section = sa.Column(sa.BigInteger)


class FormSection(BASE):
    __tablename__ = 'form_section'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(
        sa.BigInteger,
        sa.Sequence('form_section_seq', start=1, increment=1),
        primary_key=True,
        nullable=False
    )
    title = sa.Column(sa.String(512))
    description = sa.Column(sa.String(512))
    is_hidden = sa.Column(sa.Boolean)
    order = sa.Column(sa.BigInteger)
    identifier = sa.Column(sa.String(255))
    form = sa.Column(sa.BigInteger, nullable=False)


class FormSubSection(BASE):
    __tablename__ = 'form_sub_section'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(
        sa.BigInteger,
        sa.Sequence('form_sub_section_seq', start=1, increment=1),
        primary_key=True,
        nullable=False
    )
    description = sa.Column(sa.String(512))
    dynamic_field_sections = sa.Column(JSONB)
    identifier = sa.Column(sa.String(255))
    is_hidden = sa.Column(sa.Boolean)
    order = sa.Column(sa.BigInteger)
    title = sa.Column(sa.String(512))
    form_section = sa.Column(sa.BigInteger, nullable=False)


class Document(BASE, CommonColumns):
    __tablename__ = 'document'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.BigInteger, sa.Sequence('doc_seq', start=1, increment=1), primary_key=True, nullable=False)
    document_expire_time = sa.Column(sa.BigInteger)
    document_name = sa.Column(sa.String(255))
    document_path = sa.Column(sa.String(255))
    document_version_id = sa.Column(sa.String(255))
    document_size = sa.Column(sa.String(255))
    document_type = sa.Column(sa.String(255))
    document_url = sa.Column(sa.Text)
    document_preview_url = sa.Column(sa.Text)
    user = sa.Column(UUID(as_uuid=True), nullable=False)


class Physician(BASE):
    __tablename__ = 'physician'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    caqh_profile_id = sa.Column(sa.String(255))
    caqh_updated_at = sa.Column(sa.BigInteger)
    form = sa.Column(sa.BigInteger)
    onboarding = sa.Column(JSONB)
    user = sa.Column(UUID(as_uuid=True), nullable=False)


class APILedger(BASE):
    __tablename__ = 'api_ledger'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.BigInteger, sa.Sequence('api_ledger_seq', start=1, increment=1), primary_key=True, nullable=False)
    created_at = sa.Column(sa.BigInteger)
    customer_id = sa.Column(sa.String(255))
    customer_name = sa.Column(sa.String(255))
    document_version_id = sa.Column(sa.String(255))
    entity_id = sa.Column(sa.String(255))
    file_path = sa.Column(sa.String(255))
    request_date = sa.Column(sa.String(255))
    request_ip = sa.Column(sa.String(255))
    request_type = sa.Column(sa.String(255))
    user_type = sa.Column(sa.String(255))
