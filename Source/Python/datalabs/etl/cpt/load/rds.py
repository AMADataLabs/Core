import logging
import os
import psycopg2

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
LOGGER.info('Upload Successful')


class RDSCreator:

    def __init__(self):
        self.connection = psycopg2.connect(
            host=os.environ['rds_host'],
            port=os.environ['rds_port'],
            user=os.environ['rds_user'],
            password=os.environ['rds_password'],
            database=os.environ['rds_database'])

        self.cursor = self.connection.cursor()

    def create_schema(self):
        self.cursor.execute('CREATE SCHEMA IF NOT EXISTS CPT_Data')
        self.connection.commit()
        LOGGER.info('Successful')

    def create_descriptor_table(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS CPT_Data.clinician_descriptor
        (id INT PRIMARY KEY, 
        concept_id VARCHAR, 
        cpt_code CHAR(5),
        clinician_descriptor_id VARCHAR, 
        clinical_descriptor VARCHAR)""")
        self.connection.commit()
        LOGGER.info('Successful')

    def create_cpt_table(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS CPT_Data.cpt
        (id INT PRIMARY KEY, 
        cpt_code CHAR(5) UNIQUE,
        short_description CHAR(28), 
        medium_description CHAR(48),
        long_description VARCHAR)""")
        self.connection.commit()
        LOGGER.info('Successful')

    def create_modifier_type_table(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS CPT_Data.modifier_type
        (id INT PRIMARY KEY, 
        mod_type VARCHAR UNIQUE)""")
        self.connection.commit()
        LOGGER.info('Successful')

    def create_modifier_table(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS CPT_Data.modifiers
        (id INT PRIMARY KEY, 
        mod_code CHAR(2), 
        mod_type VARCHAR,
        mod_description VARCHAR)""")
        self.connection.commit()
        LOGGER.info('Successful')

    def push_cpt_table(self, file):
        self.cursor.execute("""TRUNCATE CPT_Data.cpt""")
        with open(file, 'r') as row:
            next(row)
            self.cursor.copy_from(row, 'CPT_Data.cpt', sep='\t')
        self.connection.commit()
        LOGGER.info('Successful')

    def push_descriptor_table(self, file):
        self.cursor.execute("""TRUNCATE CPT_Data.clinician_descriptor""")
        with open(file, 'r') as row:
            next(row)
            self.cursor.copy_from(row, 'CPT_Data.clinician_descriptor', sep='\t')
        self.connection.commit()
        LOGGER.info('Successful')

    def push_modifier_type_table(self):
        self.cursor.execute("""INSERT INTO CPT_Data.modifier_type 
        (id,mod_type)
        VALUES (1,'Regular'), (2,'Physical'), (3,'LevelOne'), (4,'CategoryTwo'), (5,'LevelTwo')
        """)
        self.connection.commit()
        LOGGER.info('Successful')

    def push_modifiers_table(self, file):
        self.cursor.execute("""TRUNCATE CPT_Data.modifiers""")
        with open(file, 'r') as row:
            next(row)
            self.cursor.copy_from(row, 'CPT_Data.modifiers', sep='\t')
        self.connection.commit()
        LOGGER.info('Successful')
