""" Lambda function handler for the CPT API """
import os

import psycopg2


def lambda_handler(event, context):
    connection = psycopg2.connect(
        host=os.environ.get('DATABASE_RDS_HOST'),
        port=os.environ.get('DATABASE_RDS_PORT'),
        database=os.environ.get('DATABASE_RDS_NAME'),
        user=os.environ.get('CREDENTIALS_RDS_USERNAME'),
        password=os.environ.get('CREDENTIALS_RDS_PASSWORD'),
    )

    cursor = connection.cursor()
    cursor.execute('SELECT * FROM CPT_Data.clinician_descriptor LIMIT 10')
    records = []
    for row in cursor:
        record = {
            'concept_id': row[1],
            'cpt_code': row[2],
            'clinician_descriptor_id': row[3],
            'clinical_descriptor': row[4]
        }

        records.append(record)

    return {'statusCode': 200, 'headers' : 'for authorization', 'body' : records}
