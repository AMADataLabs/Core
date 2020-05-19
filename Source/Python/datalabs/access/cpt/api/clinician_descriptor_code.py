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

    status_code, response = query_code(event, cursor)
    return {'statusCode': status_code, 'body': response}


def query_code(event, cursor):
    code_exists = check_if_code_given(event)
    if code_exists:
        requested_code = event['code']
        query = "SELECT * FROM CPT_Data.clinician_descriptor WHERE cpt_code ='{}'".format(requested_code)

        cursor.execute(query)
        if cursor.rowcount == 0:
            return 400, {requested_code: "Does Not Exist"}
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


def check_if_code_given(event):
    requested_code = event['code']
    if requested_code is None:
        return False
    else:
        return True
