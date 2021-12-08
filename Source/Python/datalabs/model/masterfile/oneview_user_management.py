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


class DatalabsFeedbackQuestions(BASE):
    __tablename__ = 'Datalabs_Feedback_Questions'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    question_text = sa.Column(sa.String, default=None)
    min_value = sa.Column(sa.String, default=None)
    max_value = sa.Column(sa.String, default=None)
    question_type = sa.Column(sa.String, default=None)
    min_description = sa.Column(sa.String, default=None)
    max_description = sa.Column(sa.String, default=None)
    question_order = sa.Column(sa.Integer, default=None)


class DatalabsFeedbackResponses(BASE):
    __tablename__ = 'Datalabs_Feedback_Responses'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    user_id = sa.Column(sa.String, default=None)
    question_id = sa.Column(sa.String, sa.ForeignKey(f"{SCHEMA}.Datalabs_Feedback_Questions.id"))
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


class Domains(BASE):
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
    department_id = sa.Column(sa.Integer, sa.ForeignKey(f"{SCHEMA}.Departments.id"))
    organization_id = sa.Column(sa.Integer, sa.ForeignKey(f"{SCHEMA}.Organization.id"))
    description = sa.Column(sa.String, default=None)
    default = sa.Column(sa.Boolean, default=None)


class GroupsResourcePermission(BASE):
    __tablename__ = 'Groups_Resource_Permission'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    group_id = sa.Column(sa.Integer, sa.ForeignKey(f"{SCHEMA}.Groups.id"))
    resource_permission_id = sa.Column(sa.Integer, sa.ForeignKey(f"{SCHEMA}.Resource_Permission.id"))


class GroupsResources(BASE):
    __tablename__ = 'Groups_Resources'
    __table_args__ = {"schema": SCHEMA}

    id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    group_id = sa.Column(sa.Integer, sa.ForeignKey(f"{SCHEMA}.Groups.id"))
    resource_id = sa.Column(sa.Integer, sa.ForeignKey(f"{SCHEMA}.Resource.id"))
    access_id = sa.Column(sa.Integer, sa.ForeignKey(f"{SCHEMA}.Access.id"))




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

# pylint: disable=pointless-string-statement
"""
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
"""
