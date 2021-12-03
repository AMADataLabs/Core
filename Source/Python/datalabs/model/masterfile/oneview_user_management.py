""" SQLAlchemy models for OneView """
import sqlalchemy as sa
from   sqlalchemy.ext.declarative import declarative_base

from   datalabs.sqlalchemy import metadata

BASE = declarative_base(metadata=metadata())
SCHEMA = 'oneview'


class Access(BASE):
    __tablename__ = 'Access'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    level = sa.Column(sa.String, default=None)


class AgeGenderMPAAnnual(BASE):
    __tablename__ = 'Age_Gender_Mpa_Annual'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    year = sa.Column(sa.String, default=None)
    gender = sa.Column(sa.String, default=None)
    age = sa.Column(sa.String, default=None)
    mpa_description = sa.Column(sa.String, default=None)
    count = sa.Column(sa.String, default=None)


class OneviewFeedbackQuestions(BASE):
    __tablename__ = 'Oneview_Feedback_Questions'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    question_text = sa.Column(sa.String, default=None)
    min_value = sa.Column(sa.String, default=None)
    max_value = sa.Column(sa.String, default=None)
    question_type = sa.Column(sa.String, default=None)
    min_description = sa.Column(sa.String, default=None)
    max_description = sa.Column(sa.String, default=None)
    question_order = sa.Column(sa.Integer, default=None)


class OneviewFeedbackResponses(BASE):
    __tablename__ = 'Oneview_Feedback_Responses'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    user_id = sa.Column(sa.String, default=None)
    question_id = sa.Column(sa.String, sa.ForeignKey(f"{SCHEMA}.Oneview_Feedback_Questions.id"))
    response = sa.Column(sa.String, default=None)
    response_time = sa.Column(sa.String, default=None)


class Departments(BASE):
    __tablename__ = 'Departments'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    name = sa.Column(sa.String, default=None)
    organization_id = sa.Column(sa.Integer, sa.ForeignKey(f"{SCHEMA}.Organization.id"))
    primary_admin = sa.Column(sa.Integer, default=None)
    phone_number = sa.Column(sa.String, default=None)
    email_id = sa.Column(sa.String, default=None)
    function = sa.Column(sa.String, default=None)
    backup_admin = sa.Column(sa.Integer, default=None)
    default = sa.Column(sa.Boolean, default=None)


class Departments(BASE):
    __tablename__ = 'Domains'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    domain_name = sa.Column(sa.String, default=None)
    can_associate = sa.Column(sa.Boolean, default=None)


class Environments(BASE):
    __tablename__ = 'Environments'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    name = sa.Column(sa.String, default=None)


class Groups(BASE):
    __tablename__ = 'Groups'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    name = sa.Column(sa.String, default=None)
    department_id = sa.Column(sa.Integer, default=None, sa.ForeignKey(f"{SCHEMA}.Departments.id"))
    organization_id = sa.Column(sa.Integer, default=None, sa.ForeignKey(f"{SCHEMA}.Organization.id"))
    description = sa.Column(sa.String, default=None)
    default = sa.Column(sa.Boolean, default=None)


class GroupsResourcePermission(BASE):
    __tablename__ = 'Groups_Resource_Permission'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    group_id = sa.Column(sa.Integer, default=None, sa.ForeignKey(f"{SCHEMA}.Groups.id"))
    resource_permission_id = sa.Column(sa.Integer, default=None, sa.ForeignKey(f"{SCHEMA}.Resource_Permission.id"))


class GroupsResources(BASE):
    __tablename__ = 'Groups_Resources'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    group_id = sa.Column(sa.Integer, default=None, sa.ForeignKey(f"{SCHEMA}.Groups.id"))
    resource_id = sa.Column(sa.Integer, default=None, sa.ForeignKey(f"{SCHEMA}.Resource.id"))
    access_id = sa.Column(sa.Integer, default=None, sa.ForeignKey(f"{SCHEMA}.Access.id"))




class OneviewFeedbackQuestions(BASE):
    __tablename__ = 'Oneview_Feedback_Questions'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    question_text = sa.Column(sa.String, default=None)
    min_value = sa.Column(sa.String, default=None)
    max_value = sa.Column(sa.String, default=None)
    question_type = sa.Column(sa.String, default=None)
    min_description = sa.Column(sa.String, default=None)
    max_description = sa.Column(sa.String, default=None)
    question_order = sa.Column(sa.Integer, default=None)


class OneviewFeedbackResponses(BASE):
    __tablename__ = 'Oneview_Feedback_Responses'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    user_id = sa.Column(sa.String, default=None)
    question_id = sa.Column(sa.String, sa.ForeignKey(f"{SCHEMA}.Oneview_Feedback_Questions.id"))
    response = sa.Column(sa.String, default=None)
    response_time = sa.Column(sa.String, default=None)

CREATE TABLE `Organization` (
  `id` int(11) NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `type_id` int(11) DEFAULT NULL,
  `category_id` int(11) DEFAULT NULL,
  `addr1` varchar(45) COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `addr2` varchar(45) COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `addr3` varchar(45) COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `city` varchar(45) COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `state` varchar(45) COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `zip` varchar(45) COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `phone` varchar(45) COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `industry` varchar(45) COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `about` varchar(1000) COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `main_contact` varchar(45) COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `org_size` varchar(45) COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `country` varchar(45) COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `source_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `org_type_fk_idx` (`type_id`),
  KEY `org_source_fk_idx` (`source_id`),
  KEY `org_type_id_fk_idx` (`type_id`),
  KEY `org_source_id_fk_idx` (`source_id`),
  KEY `org_cate_id_fk_idx` (`category_id`),
  CONSTRAINT `org_cate_id_fk` FOREIGN KEY (`category_id`) REFERENCES `Organization_Categories` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `org_source_id_fk` FOREIGN KEY (`source_id`) REFERENCES `Organization_Sources` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `org_type_id_fk` FOREIGN KEY (`type_id`) REFERENCES `Organization_Types` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `Organization_Categories` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `category` varchar(45) DEFAULT NULL,
  `category_desc` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;

CREATE TABLE `Organization_Domains` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `organization_id` int(11) DEFAULT NULL,
  `domain_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `org_domains_org_id_idx` (`organization_id`),
  KEY `org_domains_domain_id_idx` (`domain_id`),
  CONSTRAINT `org_domains_domain_id` FOREIGN KEY (`domain_id`) REFERENCES `Domains` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `org_domains_org_id` FOREIGN KEY (`organization_id`) REFERENCES `Organization` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=69 DEFAULT CHARSET=latin1;

CREATE TABLE `Organization_Sources` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `source` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1;

CREATE TABLE `Organization_Types` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `type` varchar(45) DEFAULT NULL,
  `type_desc` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;

CREATE TABLE `Physician_Type_Ethnicity_Annual` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `year` varchar(45) DEFAULT NULL,
  `physician_type` varchar(250) DEFAULT NULL,
  `race_ethnicity` varchar(250) DEFAULT NULL,
  `count` varchar(45) DEFAULT NULL,
  `gender` varchar(45) DEFAULT NULL,
  `age` varchar(250) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2127 DEFAULT CHARSET=latin1;

CREATE TABLE `Resource` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(45) COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `parent_resource_id` int(11) DEFAULT NULL,
  `ui_name` varchar(255) COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=48 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `Specialty_Mpa_Annual` (
  `id` int(11) NOT NULL,
  `year` varchar(45) DEFAULT NULL,
  `specialty_description` varchar(250) DEFAULT NULL,
  `mpa_description` varchar(250) DEFAULT NULL,
  `count` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `Tokens` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `bearer_token` varchar(45) DEFAULT NULL,
  `expiry_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `bearer_token_UNIQUE` (`bearer_token`)
) ENGINE=InnoDB AUTO_INCREMENT=4930 DEFAULT CHARSET=latin1;

CREATE TABLE `User` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `fname` varchar(45) COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `mname` varchar(45) COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `lname` varchar(45) COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `email` varchar(45) COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `department_id` int(11) DEFAULT NULL,
  `tam_id` varchar(45) COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `addr1` varchar(45) COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `addr2` varchar(45) COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `addr3` varchar(45) COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `city` varchar(45) COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `zip` varchar(45) COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `phone` varchar(45) COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `state` varchar(45) COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `user_name` varchar(45) COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `is_admin` tinyint(4) DEFAULT NULL,
  `is_active` tinyint(4) DEFAULT NULL,
  `royalty_portal_access` tinyint(4) DEFAULT NULL,
  `last_updated_by` varchar(45) COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `is_super_admin` tinyint(4) DEFAULT NULL,
  `devportal_access` tinyint(4) DEFAULT NULL,
  `org_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=144 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `User_Filters` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) DEFAULT NULL,
  `filter_name` varchar(45) DEFAULT NULL,
  `filter_criteria` json DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_filters_user_id_fk_idx` (`user_id`),
  CONSTRAINT `user_filters_user_id_fk` FOREIGN KEY (`user_id`) REFERENCES `User` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=latin1;

CREATE TABLE `User_Group_Assignment` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) DEFAULT NULL,
  `group_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ug_user_id_fk_idx` (`user_id`),
  KEY `ug_group_id_fk_idx` (`group_id`),
  CONSTRAINT `ug_group_id_fk` FOREIGN KEY (`group_id`) REFERENCES `Groups` (`id`),
  CONSTRAINT `ug_user_id_fk` FOREIGN KEY (`user_id`) REFERENCES `User` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1216 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `User_Saved_Columns` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `name` varchar(200) NOT NULL,
  `columns` json NOT NULL,
  PRIMARY KEY (`id`),
  KEY `usc_user_id_fk_idx` (`user_id`),
  CONSTRAINT `usc_user_id_fk` FOREIGN KEY (`user_id`) REFERENCES `User` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=40 DEFAULT CHARSET=latin1;



################################################################
# Physician Tables
################################################################

class Physician(BASE):
    __tablename__ = 'physician'
    __table_args__ = (
        sa.ForeignKeyConstraint(
            ['federal_information_processing_standard_state',
             'federal_information_processing_standard_county'],
            ['oneview.federal_information_processing_standard_county.state',
             'oneview.federal_information_processing_standard_county.county']
        ),
        {"schema": SCHEMA}
    )

    medical_education_number = sa.Column(sa.String, primary_key=True)
    address_type = sa.Column(sa.String)
    mailing_name = sa.Column(sa.String)
    last_name = sa.Column(sa.String)
    first_name = sa.Column(sa.String)
    middle_name = sa.Column(sa.String)
    name_suffix = sa.Column(sa.String)
    preferred_address_2 = sa.Column(sa.String)
    preferred_address_1 = sa.Column(sa.String)
    city = sa.Column(sa.String)
    state = sa.Column(sa.String)  #, sa.ForeignKey("oneview.state.id")) - 2-letter codes don't match numberical IDs
    zipcode = sa.Column(sa.String)
    sector = sa.Column(sa.String)
    carrier_route = sa.Column(sa.String)
    address_undeliverable = sa.Column(sa.String)
    federal_information_processing_standard_county = sa.Column(sa.String)
    federal_information_processing_standard_state = sa.Column(sa.String)
    printer_control_code_begin = sa.Column(sa.String)
    barcode_zipcode = sa.Column(sa.String)
    barcode_zipcode_plus_4 = sa.Column(sa.String)
    delivery_point = sa.Column(sa.String)
    check_digit = sa.Column(sa.String)
    printer_control_code_end = sa.Column(sa.String)
    census_region = sa.Column(sa.String)
    census_division = sa.Column(sa.String)
    census_group = sa.Column(sa.String)
    census_tract = sa.Column(sa.String)
    census_suffix = sa.Column(sa.String)
    census_block_group = sa.Column(sa.String)
    metropolitan_statistical_area_population = sa.Column(sa.String)
    micro_metro_indicator = sa.Column(sa.String)
    core_based_statistical_area = sa.Column(sa.String, sa.ForeignKey("oneview.core_based_statistical_area.id"))
    core_based_statistical_area_division = sa.Column(sa.String)
    degree_type = sa.Column(sa.String)
    birth_year = sa.Column(sa.String)
    birth_city = sa.Column(sa.String)
    birth_state = sa.Column(sa.String)
    birth_country = sa.Column(sa.String)
    gender = sa.Column(sa.String)
    telephone_number = sa.Column(sa.String)
    presumed_dead = sa.Column(sa.String)
    fax_number = sa.Column(sa.String)
    type_of_practice = sa.Column(sa.String, sa.ForeignKey("oneview.type_of_practice.id"))
    present_employment = sa.Column(sa.String, sa.ForeignKey("oneview.present_employment.id"))
    primary_specialty = sa.Column(sa.String, sa.ForeignKey("oneview.specialty.id"))
    secondary_specialty = sa.Column(sa.String, sa.ForeignKey("oneview.specialty.id"))
    major_professional_activity = sa.Column(sa.String, sa.ForeignKey("oneview.major_professional_activity.id"))
    physician_recognition_award_recipient = sa.Column(sa.String)
    physician_recognition_award_expiration_date = sa.Column(sa.String)
    graduate_medical_education_confirm = sa.Column(sa.String)
    from_date = sa.Column(sa.String)
    end_date = sa.Column(sa.String)
    year_in_program = sa.Column(sa.String)
    post_graduate_year = sa.Column(sa.String)
    graduate_medical_education_primary_specialty = sa.Column(sa.String)
    graduate_medical_education_secondary_specialty = sa.Column(sa.String)
    training_type = sa.Column(sa.String)
    graduate_medical_education_hospital_state = sa.Column(sa.String)
    graduate_medical_education_hospital = sa.Column(sa.String)
    medical_school_state = sa.Column(sa.String)
    medical_school = sa.Column(sa.String)
    medical_school_graduation_year = sa.Column(sa.String)
    no_contact_type = sa.Column(sa.String)
    no_web = sa.Column(sa.String)
    physician_data_restriction_program = sa.Column(sa.String)
    physician_data_restriction_program_date = sa.Column(sa.String)
    polo_address_2 = sa.Column(sa.String)
    polo_address_1 = sa.Column(sa.String)
    polo_city = sa.Column(sa.String)
    polo_state = sa.Column(sa.String)
    polo_zipcode = sa.Column(sa.String)
    polo_sector = sa.Column(sa.String)
    polo_carrier_route = sa.Column(sa.String)
    most_recent_former_last_name = sa.Column(sa.String)
    most_recent_former_middle_name = sa.Column(sa.String)
    most_recent_former_first_name = sa.Column(sa.String)
    next_most_recent_former_last_name = sa.Column(sa.String)
    next_most_recent_former_middle_name = sa.Column(sa.String)
    next_most_recent_former_first_name = sa.Column(sa.String)
    national_provider_identifier = sa.Column(sa.String)
    party_id = sa.Column(sa.String)
    entity_id = sa.Column(sa.String)
    race_ethnicity = sa.Column(sa.String)
    membership_status = sa.Column(sa.String)
    type = sa.Column(sa.String)
    has_email = sa.Column(sa.Boolean)
    no_release = sa.Column(sa.Boolean)


class ResidencyProgram(BASE):
    __tablename__ = 'residency_program'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    specialty = sa.Column(sa.String)
    institution_control = sa.Column(sa.String)
    sequence_number = sa.Column(sa.String)
    federal_code = sa.Column(sa.String)
    region_code = sa.Column(sa.String)
    acgme_accredited = sa.Column(sa.Boolean)
    name = sa.Column(sa.String)
    web_address = sa.Column(sa.String)
    contact_director = sa.Column(sa.Boolean)
    accreditation_status = sa.Column(sa.String)
    accreditation_effective_date = sa.Column(sa.Date)
    initial_accreditation_date = sa.Column(sa.Date)
    accreditation_length = sa.Column(sa.String)
    duration = sa.Column(sa.String)
    government_affiliated = sa.Column(sa.Boolean)
    graduate_medical_education_equivalent_years = sa.Column(sa.String)
    preliminary_years_required = sa.Column(sa.String)
    preliminary_positions_offered = sa.Column(sa.Boolean)
    type = sa.Column(sa.String)
    max_residents_accepted_increase = sa.Column(sa.Integer)
    percent_at_primary_site = sa.Column(sa.String)
    primary_site = sa.Column(sa.String)
    core_program = sa.Column(sa.String)
    medical_records = sa.Column(sa.Boolean)
    official_address = sa.Column(sa.Boolean)
    uses_sfmatch = sa.Column(sa.Boolean)
    other_match_indicator = sa.Column(sa.Boolean)
    other_match = sa.Column(sa.String)
    additional_education_accreditation_length = sa.Column(sa.Boolean)
    last_update_date = sa.Column(sa.Date)
    last_update_type = sa.Column(sa.String)
    american_osteopathic_association_indicator = sa.Column(sa.Boolean)
    american_osteopathic_association_program = sa.Column(sa.String)
    osteopathic_principles = sa.Column(sa.Boolean)
    address_1 = sa.Column(sa.String)
    address_2 = sa.Column(sa.String)
    address_3 = sa.Column(sa.String)
    city = sa.Column(sa.String)
    state = sa.Column(sa.String)
    zipcode = sa.Column(sa.String)
    primary_clinical_location = sa.Column(sa.String)
    institution = sa.Column(sa.String, sa.ForeignKey("oneview.residency_program_institution.id"))


class ResidencyProgramPersonnelMember(BASE):
    __tablename__ = 'residency_program_personnel_member'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    program = sa.Column(sa.String, sa.ForeignKey("oneview.residency_program.id"), nullable=False)
    first_name = sa.Column(sa.String)
    middle_name = sa.Column(sa.String)
    last_name = sa.Column(sa.String)
    suffix_name = sa.Column(sa.String)
    degree_1 = sa.Column(sa.String)
    degree_2 = sa.Column(sa.String)
    degree_3 = sa.Column(sa.String)
    last_update_date = sa.Column(sa.Date)


class ResidencyProgramInstitution(BASE):
    __tablename__ = 'residency_program_institution'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    name = sa.Column(sa.String)
    affiliation = sa.Column(sa.String)
    last_update_date = sa.Column(sa.Date)


class Business(BASE):
    __tablename__ = 'business'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.String, primary_key=True)
    name = sa.Column(sa.String, nullable=False)
    doing_business_as = sa.Column(sa.String)
    iqvia_address_id = sa.Column(sa.String, nullable=False)
    physical_address_1 = sa.Column(sa.String, nullable=False)
    physical_address_2 = sa.Column(sa.String)
    physical_city = sa.Column(sa.String, nullable=False)
    physical_state = sa.Column(sa.String, nullable=False)
    physical_zipcode = sa.Column(sa.String, nullable=False)
    postal_address_1 = sa.Column(sa.String, nullable=False)
    postal_address_2 = sa.Column(sa.String)
    postal_city = sa.Column(sa.String, nullable=False)
    postal_state = sa.Column(sa.String, nullable=False)
    postal_zipcode = sa.Column(sa.String, nullable=False)
    phone = sa.Column(sa.String)
    fax = sa.Column(sa.String)
    website = sa.Column(sa.String)
    latitude = sa.Column(sa.String)
    longitude = sa.Column(sa.String)
    owner_status = sa.Column(sa.String, sa.ForeignKey("oneview.owner_status.id"))
    profit_status = sa.Column(sa.String, sa.ForeignKey("oneview.profit_status.id"))
    primary_class_of_trade = sa.Column(sa.String, nullable=False)
    class_of_trade_classification = sa.Column(sa.String, sa.ForeignKey("oneview.class_of_trade_classification.id"))
    class_of_trade_classification_description = sa.Column(sa.String)
    class_of_trade_facility_type = sa.Column(sa.String, sa.ForeignKey("oneview.class_of_trade_facility.id"))
    class_of_trade_facility_type_description = sa.Column(sa.String)
    class_of_trade_specialty = sa.Column(sa.String, sa.ForeignKey("oneview.class_of_trade_specialty.id"))
    class_of_trade_specialty_description = sa.Column(sa.String)
    record_type = sa.Column(sa.String, nullable=False)
    total_licensed_beds = sa.Column(sa.String)
    total_census_beds = sa.Column(sa.String)
    total_staffed_beds = sa.Column(sa.String)
    teaching_hospital = sa.Column(sa.String)
    hospital_care = sa.Column(sa.String)
    metropolitan_statistical_area = sa.Column(sa.String)
    federal_information_processing_standard_state = sa.Column(sa.String)
    federal_information_processing_standard_county = sa.Column(sa.String)
    number_of_providers = sa.Column(sa.String)
    electronic_medical_record = sa.Column(sa.String)
    electronically_prescribe = sa.Column(sa.String)
    pay_for_performance = sa.Column(sa.String)
    deactivation_reason = sa.Column(sa.String)
    replacement_business = sa.Column(sa.String)
    status_indicator = sa.Column(sa.String, nullable=False)
    batch_business_date = sa.Column(sa.Date, sa.ForeignKey("oneview.iqvia_update.date"))


class Provider(BASE):
    __tablename__ = 'provider'
    __table_args__ = {"schema": SCHEMA}

    medical_education_number = sa.Column(sa.String, sa.ForeignKey("oneview.physician.medical_education_number"),
                                         primary_key=True)
    iqvia_provider_id = sa.Column(sa.String)
    first_name = sa.Column(sa.String)
    middle_name = sa.Column(sa.String)
    last_name = sa.Column(sa.String)
    suffix = sa.Column(sa.String)
    designation = sa.Column(sa.String)
    gender = sa.Column(sa.String)
    role = sa.Column(sa.String)
    primary_specialty = sa.Column(sa.String)
    secondary_specialty = sa.Column(sa.String)
    tertiary_specialty = sa.Column(sa.String)
    primary_profession = sa.Column(sa.String)
    primary_profession_description = sa.Column(sa.String)
    unique_physician_identification_number = sa.Column(sa.String)
    national_provider_identifier = sa.Column(sa.String)
    status_description = sa.Column(sa.String)
    batch_business_date = sa.Column(sa.Date, sa.ForeignKey("oneview.iqvia_update.date"))


class ProviderAffiliation(BASE):
    __tablename__ = 'provider_affiliation'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    business = sa.Column(sa.String, sa.ForeignKey("oneview.business.id"))
    medical_education_number = sa.Column(sa.String, sa.ForeignKey("oneview.physician.medical_education_number"))
    type = sa.Column(sa.String, sa.ForeignKey("oneview.provider_affiliation_type.id"))
    description = sa.Column(sa.String)
    primary = sa.Column(sa.String)
    rank = sa.Column(sa.String)
    group = sa.Column(sa.String, sa.ForeignKey("oneview.provider_affiliation_group.id"))
    group_description = sa.Column(sa.String)
    batch_business_date = sa.Column(sa.Date, sa.ForeignKey("oneview.iqvia_update.date"))


################################################################
# Credentialing Tables
################################################################

class CredentialingCustomer(BASE):
    __tablename__ = 'credentialing_customer'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    number = sa.Column(sa.String, nullable=False)
    name = sa.Column(sa.String, nullable=True)
    type = sa.Column(sa.String, nullable=False)
    type_description = sa.Column(sa.String, nullable=False)
    category = sa.Column(sa.String, nullable=True)
    category_description = sa.Column(sa.String, nullable=True)
    current_indicator = sa.Column(sa.String, nullable=False)
    address_1 = sa.Column(sa.String, nullable=True)
    address_2 = sa.Column(sa.String, nullable=True)
    address_3 = sa.Column(sa.String, nullable=True)
    city = sa.Column(sa.String, nullable=True)
    state = sa.Column(sa.String, nullable=True)
    zipcode = sa.Column(sa.String, nullable=True)
    phone_number = sa.Column(sa.String, nullable=True)
    company_name = sa.Column(sa.String, nullable=True)


class CredentialingOrder(BASE):
    __tablename__ = 'credentialing_order'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    customer = sa.Column(sa.Integer, sa.ForeignKey("oneview.credentialing_customer.id"), nullable=False)
    product = sa.Column(sa.Integer, sa.ForeignKey("oneview.credentialing_product.id"), nullable=False)
    number = sa.Column(sa.String, nullable=False)
    medical_education_number = sa.Column(sa.String, sa.ForeignKey("oneview.physician.medical_education_number"),
                                         nullable=False)
    date = sa.Column(sa.String, nullable=False)
    quantity = sa.Column(sa.String, nullable=False)
    unique_physician_identification_number = sa.Column(sa.String, nullable=True)


################################################################
# Statistics Tables
################################################################

class ZipCode(BASE):
    __tablename__ = 'zip_code'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    zip_code = sa.Column(sa.String, nullable=False)
    state = sa.Column(sa.String, nullable=False)
    city = sa.Column(sa.String, nullable=False)
    type = sa.Column(sa.String, nullable=False)
    county_federal_information_processing = sa.Column(sa.String, nullable=False)
    latitude = sa.Column(sa.String, nullable=False)
    longitude = sa.Column(sa.String, nullable=False)
    metropolitan_statistical_area = sa.Column(sa.String, nullable=False)
    primary_metropolitan_statistical_area = sa.Column(sa.String, nullable=False)


class County(BASE):
    __tablename__ = 'county'
    __table_args__ = {"schema": SCHEMA}

    federal_information_processing_standard_code = sa.Column(sa.String, primary_key=True, nullable=False)
    county_name = sa.Column(sa.String, nullable=False)
    state = sa.Column(sa.String, nullable=False)
    time_zone = sa.Column(sa.String, nullable=False)
    county_type = sa.Column(sa.String, nullable=False)
    county_seat = sa.Column(sa.String, nullable=False)
    name_type = sa.Column(sa.String, nullable=False)
    elevation = sa.Column(sa.Integer, nullable=False)
    person_per_household = sa.Column(sa.Integer, nullable=False)
    population = sa.Column(sa.Integer, nullable=False)
    area = sa.Column(sa.Integer, nullable=False)
    households = sa.Column(sa.Integer, nullable=False)
    white = sa.Column(sa.Integer, nullable=False)
    black = sa.Column(sa.Integer, nullable=False)
    hispanic = sa.Column(sa.Integer, nullable=False)
    average_income = sa.Column(sa.String, nullable=False)
    average_house = sa.Column(sa.Integer, nullable=False)


class AreaCode(BASE):
    __tablename__ = 'area_code'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    area_code = sa.Column(sa.String, nullable=False)
    prefix = sa.Column(sa.String, nullable=False)
    latitude = sa.Column(sa.String, nullable=False)
    longitude = sa.Column(sa.String, nullable=False)


class Census(BASE):
    __tablename__ = 'census'
    __table_args__ = {"schema": SCHEMA}

    zip_code = sa.Column(sa.String, primary_key=True, nullable=False)
    population = sa.Column(sa.Integer, nullable=False)
    urban = sa.Column(sa.Integer, nullable=False)
    suburban = sa.Column(sa.Integer, nullable=False)
    farm = sa.Column(sa.Integer, nullable=False)
    non_farm = sa.Column(sa.Integer, nullable=False)
    white = sa.Column(sa.Integer, nullable=False)
    black = sa.Column(sa.Integer, nullable=False)
    indian = sa.Column(sa.Integer, nullable=False)
    asian = sa.Column(sa.Integer, nullable=False)
    hawaiian = sa.Column(sa.Integer, nullable=False)
    race_other = sa.Column(sa.Integer, nullable=False)
    hispanic = sa.Column(sa.Integer, nullable=False)
    age_0_to_4 = sa.Column(sa.Integer, nullable=False)
    age_5_to_9 = sa.Column(sa.Integer, nullable=False)
    age_10_to_14 = sa.Column(sa.Integer, nullable=False)
    age_15_to_17 = sa.Column(sa.Integer, nullable=False)
    age_18_to_19 = sa.Column(sa.Integer, nullable=False)
    age_20 = sa.Column(sa.Integer, nullable=False)
    age_21 = sa.Column(sa.Integer, nullable=False)
    age_22_to_24 = sa.Column(sa.Integer, nullable=False)
    age_25_to_29 = sa.Column(sa.Integer, nullable=False)
    age_30_to_34 = sa.Column(sa.Integer, nullable=False)
    age_35_to_39 = sa.Column(sa.Integer, nullable=False)
    age_40_to_44 = sa.Column(sa.Integer, nullable=False)
    age_45_to_49 = sa.Column(sa.Integer, nullable=False)
    age_50_to_54 = sa.Column(sa.Integer, nullable=False)
    age_55_to_59 = sa.Column(sa.Integer, nullable=False)
    age_60_to_61 = sa.Column(sa.Integer, nullable=False)
    age_62_to_64 = sa.Column(sa.Integer, nullable=False)
    age_65_to_66 = sa.Column(sa.Integer, nullable=False)
    age_67_to_69 = sa.Column(sa.Integer, nullable=False)
    age_70_to_74 = sa.Column(sa.Integer, nullable=False)
    age_75_to_79 = sa.Column(sa.Integer, nullable=False)
    age_80_to_84 = sa.Column(sa.Integer, nullable=False)
    age_85_plus = sa.Column(sa.Integer, nullable=False)
    education_below_9 = sa.Column(sa.Integer, nullable=False)
    education_9_to_12 = sa.Column(sa.Integer, nullable=False)
    education_high_school = sa.Column(sa.Integer, nullable=False)
    education_some_college = sa.Column(sa.Integer, nullable=False)
    education_association = sa.Column(sa.Integer, nullable=False)
    education_bachelor = sa.Column(sa.Integer, nullable=False)
    education_professional = sa.Column(sa.Integer, nullable=False)
    household_income = sa.Column(sa.Integer, nullable=False)
    per_person_income = sa.Column(sa.Integer, nullable=False)
    house_value = sa.Column(sa.Integer, nullable=False)


class CoreBasedStatisticalAreaMelissa(BASE):
    __tablename__ = 'core_based_statistical_area_melissa'
    __table_args__ = {"schema": SCHEMA}

    code = sa.Column(sa.String, primary_key=True, nullable=False)
    type = sa.Column(sa.String, nullable=False)
    title = sa.Column(sa.String, nullable=False)
    level = sa.Column(sa.String, nullable=False)
    status = sa.Column(sa.String, nullable=False)


class ZipCodeCoreBasedStatisticalArea(BASE):
    __tablename__ = 'zip_code_core_based_statistical_areas'
    __table_args__ = {"schema": SCHEMA}

    zip_code = sa.Column(sa.String, primary_key=True, nullable=False)
    core_based_statistical_area = sa.Column(sa.String, nullable=False)
    division = sa.Column(sa.String, nullable=False)


class MetropolitanStatisticalArea(BASE):
    __tablename__ = 'metropolitan_statistical_area'
    __table_args__ = {"schema": SCHEMA}

    code = sa.Column(sa.String, primary_key=True, nullable=False)
    type = sa.Column(sa.String, nullable=False)
    name = sa.Column(sa.String, nullable=False)
    consolidated_metropolitan_statistical_area = sa.Column(sa.String, nullable=False)
    population = sa.Column(sa.Integer, nullable=False)


class HistoricalResident(BASE):
    __tablename__ = 'historical_resident'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.String, primary_key=True)
    medical_education_number = sa.Column(sa.String, sa.ForeignKey("oneview.physician.medical_education_number"),
                                         nullable=False)
    institution_code = sa.Column(sa.String, nullable=False)
    specialty = sa.Column(sa.String, nullable=False)
    training_type = sa.Column(sa.String, nullable=True)
    start_year = sa.Column(sa.Integer, nullable=False)
    end_year = sa.Column(sa.Integer, nullable=False)


class IqviaUpdate(BASE):
    __tablename__ = 'iqvia_update'
    __table_args__ = {"schema": SCHEMA}

    date = sa.Column(sa.Date, unique=True, primary_key=True, nullable=False)


################################################################
# Linking Tables
################################################################

class CredentialingCustomerInstitution(BASE):
    __tablename__ = 'credentialing_customer_institution'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.Integer, primary_key=True)
    customer = sa.Column(sa.Integer, sa.ForeignKey("oneview.credentialing_customer.id"), nullable=False)
    residency_program_institution = sa.Column(sa.String,
                                              sa.ForeignKey("oneview.residency_program_institution.id"),
                                              nullable=False)


class CredentialingCustomerBusiness(BASE):
    __tablename__ = 'credentialing_customer_business'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.Integer, primary_key=True)
    customer = sa.Column(sa.Integer, sa.ForeignKey("oneview.credentialing_customer.id"), nullable=False)
    business = sa.Column(sa.String, sa.ForeignKey("oneview.business.id"), nullable=False)


class ResidencyProgramPhysician(BASE):
    __tablename__ = 'residency_program_physician'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.String, primary_key=True)
    program = sa.Column(sa.String, sa.ForeignKey("oneview.residency_program.id"), nullable=False, unique=True)
    medical_education_number = sa.Column(
        sa.String,
        sa.ForeignKey("oneview.physician.medical_education_number"),
        nullable=False
    )


class CorporateParentBusiness(BASE):
    __tablename__ = 'corporate_parent_business'
    __table_args__ = {"schema": SCHEMA}

    child = sa.Column(sa.String, sa.ForeignKey("oneview.business.id"), primary_key=True, nullable=False)
    parent = sa.Column(sa.String, sa.ForeignKey("oneview.business.id"))


class SubsidiaryOwnerBusiness(BASE):
    __tablename__ = 'subsidiary_owner_business'
    __table_args__ = {"schema": SCHEMA}

    subsidiary = sa.Column(sa.String, sa.ForeignKey("oneview.business.id"), primary_key=True, nullable=False)
    owner = sa.Column(sa.String, sa.ForeignKey("oneview.business.id"))


################################################################
# Reference Tables
################################################################

class CredentialingProduct(BASE):
    __tablename__ = 'credentialing_product'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.Integer, primary_key=True)
    description = sa.Column(sa.String, nullable=False)


class TypeOfPractice(BASE):
    __tablename__ = 'type_of_practice'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    description = sa.Column(sa.String, nullable=False)


class PresentEmployment(BASE):
    __tablename__ = 'present_employment'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    description = sa.Column(sa.String, nullable=False)


class MajorProfessionalActivity(BASE):
    __tablename__ = 'major_professional_activity'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    description = sa.Column(sa.String, nullable=False)


class FederalInformationProcessingStandardCounty(BASE):
    __tablename__ = 'federal_information_processing_standard_county'
    __table_args__ = (
        sa.UniqueConstraint('state', 'county'),
        {"schema": SCHEMA}
    )
    id = sa.Column(sa.String, primary_key=True, nullable=False)
    state = sa.Column(sa.String, nullable=False)
    county = sa.Column(sa.String, nullable=False)
    description = sa.Column(sa.String, nullable=False)


class CoreBasedStatisticalArea(BASE):
    __tablename__ = 'core_based_statistical_area'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    description = sa.Column(sa.String, nullable=False)


class Specialty(BASE):
    __tablename__ = 'specialty'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    description = sa.Column(sa.String, nullable=False)


class State(BASE):
    __tablename__ = 'state'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    description = sa.Column(sa.String, nullable=False)


class ClassOfTradeClassification(BASE):
    __tablename__ = 'class_of_trade_classification'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    description = sa.Column(sa.String, nullable=False)


class ClassOfTradeSpecialty(BASE):
    __tablename__ = 'class_of_trade_specialty'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    description = sa.Column(sa.String, nullable=False)


class ClassOfTradeFacilityType(BASE):
    __tablename__ = 'class_of_trade_facility'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    description = sa.Column(sa.String, nullable=False)


class ProviderAffiliationGroup(BASE):
    __tablename__ = 'provider_affiliation_group'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    description = sa.Column(sa.String, nullable=False)


class ProviderAffiliationType(BASE):
    __tablename__ = 'provider_affiliation_type'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    description = sa.Column(sa.String, nullable=False)


class ProfitStatus(BASE):
    __tablename__ = 'profit_status'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    description = sa.Column(sa.String, nullable=False)


class OwnerStatus(BASE):
    __tablename__ = 'owner_status'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    description = sa.Column(sa.String, nullable=False)


class MedicalSchool(BASE):
    __tablename__ = 'medical_school'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    description = sa.Column(sa.String, nullable=False)
