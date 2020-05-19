import psycopg2

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

    status_code, response = query_id(event, cursor)
    return {'statusCode': status_code, 'body': response}


def query_id(event, cursor):
    id_exists = check_if_id_given(event)
    if id_exists:
        requested_id = event['id']
        query = "SELECT * FROM CPT_Data.clinician_descriptor WHERE concept_id='{}'".format(requested_id)
        cursor.execute(query)

        if cursor.rowcount == 0:
            return 400, {requested_id: "Does Not Exist"}
        else:
            records = []
            for row in cursor:
                record = {
                    'concept_id': row[1],
                    'cpt_code': row[2],
                    'clinician_descriptor_id': row[3],
                    'clinical_descriptor': row[4]

                }
                records.append(record)
            return 200, records
    else:
        return 400, {"Error": "No code given"}


def check_if_id_given(event):
    requested_id = event['id']
    if requested_id is None:
        return False
    else:
        return True
