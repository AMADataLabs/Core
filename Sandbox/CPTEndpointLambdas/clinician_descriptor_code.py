import psycopg2

import os


def lambda_handler(event, context):
    connection = psycopg2.connect(
        host=os.environ.get('DATABASE_RDS_HOST'),
        port=os.environ.get('DATABASE_RDS_PORT'),
        database=os.environ.get('DATABASE_RDS_NAME'),
        user=os.environ.get('CREDENTIALS_RDS_USERNAME'),
        password=os.environ.get('CREDENTIALS_RDS_PASSWORD'),
    )

    cursor = connection.cursor()
    response = query_id(connection, cursor)

    return {'statusCode': 200, 'headers': 'auth', 'body': response}


def query_id(event,cursor):
    requested_code = str(event['code'])
    query = "SELECT * FROM CPT_Data.clinician_descriptor WHERE cpt_code='{}'".format(requested_code)
    cursor.execute(query)
    records = []
    for row in cursor:
        record = {
            'concept_id': row[1],
            'cpt_code': row[2],
            'clinician_descriptor_id': row[3],
            'clinical_descriptor': row[4]

        }
        records.append(record)

    return records
