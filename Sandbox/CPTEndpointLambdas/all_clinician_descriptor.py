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
    if 'keyword' in list(event.keys()):
        response = query_keyword(event, cursor)

    elif "since" in list(event.keys()):
        response = query_date(event, cursor)

    else:
        response = query_all(cursor)

    return response


def query_all(cursor):
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

    return records


def query_keyword(event, cursor):
    records = []
    keyword = event['keyword'].upper()
    query = "SELECT * FROM CPT_Data.clinician_descriptor WHERE clinical_descriptor LIKE '%{}%'".format(keyword)
    cursor.execute(query)
    for row in cursor:
        record = {
            'concept_id': row[1],
            'cpt_code': row[2],
            'clinician_descriptor_id': row[3],
            'clinical_descriptor': row[4]

        }

        records.append(record)
    return records


def query_date(date, cursor):
    return 'test'
