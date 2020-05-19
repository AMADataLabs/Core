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

    status_code, response = query_event(event, cursor)
    return {'statusCode': status_code, 'body': response}


def query_event(event, cursor):
    event_type = check_event(event)
    if event_type == 'keyword':
        status, body = query_keyword(event, cursor)
        return status, body
    elif event_type == 'since':
        status, body = query_date(event, cursor)
        return status, body
    elif event_type == 'since_and_keyword':
        status, body = query_date_keyword(event, cursor)
        return status, body
    elif event_type == 'no_filters':
        status, body = query_all(cursor)
        return status, body


def check_event(event):
    if 'keyword' in list(event.keys()) and 'since' not in list(event.keys()):
        response = 'keyword'
    elif 'keyword' not in list(event.keys()) and 'since' in list(event.keys()):
        response = 'since'
    elif 'keyword' in list(event.keys()) and 'since' in list(event.keys()):
        response = 'since_and_keyword'
    else:
        response = 'no_filters'

    return response


def query_keyword(event, cursor):
    all_rows = []
    keyword = event['keyword'].upper()
    query = "SELECT * FROM CPT_Data.clinician_descriptor WHERE clinical_descriptor LIKE '%{}%'".format(keyword)
    cursor.execute(query)

    if cursor.rowcount == 0:
        return 400, {event['keyword']: "Not Found"}
    else:
        for row in cursor:
            record = {
                'concept_id': row[1],
                'cpt_code': row[2],
                'clinician_descriptor_id': row[3],
                'clinical_descriptor': row[4]

            }

            all_rows.append(record)

        return 200, all_rows


def query_date(event, cursor):
    return 200, {"In": "Progress"}


def query_date_keyword(event, cursor):
    return 200, {"In": "Progress"}


def query_all(cursor):
    cursor.execute('SELECT * FROM CPT_Data.clinician_descriptor LIMIT 10')
    all_rows = []
    for row in cursor:
        record = {
            'concept_id': row[1],
            'cpt_code': row[2],
            'clinician_descriptor_id': row[3],
            'clinical_descriptor': row[4]

        }
        all_rows.append(record)

    return 200, all_rows