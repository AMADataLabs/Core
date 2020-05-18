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
    response = check_event(event, cursor)

    return {'statusCode': 200, 'body': response}


def check_event(event, cursor):
    if 'length' in list(event.keys()):
        response = query_length(event, cursor)
    else:
        response = query_all(event, cursor)
    return response


def query_length(event, cursor):
    length = event['length'] + str('_description')
    requested_id = event['code']
    query = "SELECT cpt_code, {} FROM CPT_Data.cpt WHERE cpt_code= {}".format(length, requested_id)
    record_row = {}
    cursor.execute(query)

    for row in cursor:
        record_row = {
            'cpt_code': row[0],
            length: row[1]
        }

    return record_row


def query_all(event, cursor):
    requested_id = event['code']
    query = "SELECT * FROM CPT_Data.cpt WHERE cpt_code= '{}'".format(requested_id)
    cursor.execute(query)
    record_row = {}
    for row in cursor:
        record_row = {
            'cpt_code': row[1],
            'short_description': row[2],
            'medium_description': row[3],
            'long_description': row[4]

        }
    return record_row
