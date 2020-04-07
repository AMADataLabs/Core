import psycopg2
import sqlite3
import boto


conn = boto.connect_s3('ap-southeast-2')
connection = psycopg2.connect(
    host='database-test-ui.c3mn4zysffxi.us-east-1.rds.amazonaws.com',
    port=5432,
    user='DataLabs_UI',
    password='hsgdatalabs',
    database='sample'
)
cursor = connection.cursor()


def create_tables():
    cursor.execute('CREATE SCHEMA IF NOT EXISTS CPT_Data')
    connection.commit()

    # ClinicianDescriptor table
    cursor.execute("""CREATE TABLE IF NOT EXISTS CPT_Data.clinician_descriptor
    (id INT PRIMARY KEY, 
    concept_id VARCHAR, 
    cpt_code CHAR(5),
    clinician_descriptor_id VARCHAR, 
    clinical_descriptor VARCHAR)""")

    # CPT table
    cursor.execute("""CREATE TABLE IF NOT EXISTS CPT_Data.cpt
    (id INT PRIMARY KEY, 
    cpt_code CHAR(5) UNIQUE,
    short_description CHAR(28), 
    medium_description CHAR(48),
    long_description VARCHAR)""")

    # ModifierType table
    cursor.execute("""CREATE TABLE IF NOT EXISTS CPT_Data.modifier_type
    (id INT PRIMARY KEY, 
    mod_type VARCHAR UNIQUE)""")

    # Modifier table
    cursor.execute("""CREATE TABLE IF NOT EXISTS CPT_Data.modifiers
    (id INT PRIMARY KEY, 
    mod_code CHAR(2), 
    mod_type VARCHAR,
    mod_description VARCHAR

    )""")

    connection.commit()
    push_data()


def push_data():
    # push CPT_table csv file into table
    cursor.execute("""TRUNCATE CPT_Data.cpt, CPT_Data.clinician_descriptor,CPT_Data.modifiers""")
    with open('cpt_table.py.csv', 'r') as row:
        next(row)
        cursor.copy_from(row, 'CPT_Data.cpt', sep='\t')

    # push ClinicianDescriptor csv file into table
    with open('ClinicianDescriptor.csv', 'r') as row:
        next(row)
        cursor.copy_from(row, 'CPT_Data.clinician_descriptor', sep='\t')

    cursor.execute("""INSERT INTO CPT_Data.modifier_type 
    (id,mod_type)
    VALUES (1,'Regular'), (2,'Physical'), (3,'LevelOne'), (4,'CategoryTwo'), (5,'LevelTwo')
    """)

    # push ClinicianDescriptor csv file into table
    with open('modifiers.csv', 'r') as row:
        next(row)
        cursor.copy_from(row, 'CPT_Data.modifiers', sep='\t')

    connection.commit()


def get_s3_files():
    s3 = boto3.client('s3')
    s3.download_file('ama-hsg-datalabs-datalake-ingestion-sandbox', key, 'db1.csv')
    s3.download_file('ama-hsg-datalabs-datalake-ingestion-sandbox', key, 'db2.csv')
    s3.download_file('ama-hsg-datalabs-datalake-ingestion-sandbox', key, 'db3.csv')
    create_tables()

def main():
    get_s3_files()
    os.remove('db1.csv')
    os.remove('db2.csv')
    os.remove('db3.csv')

if __name__ == "__main__":
    main()
