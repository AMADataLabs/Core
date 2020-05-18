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
    response = check_event(event, cursor)

    return {'statusCode': 200, 'body': response}


def check_event(event, cursor):
    if 'keyword' in list(event.keys()) and 'length' in list(event.keys()):
        response = query_length_keyword(event, cursor)
    elif 'keyword' in list(event.keys()) and 'length' not in list(event.keys()):
        response = query_keyword(event, cursor)
    elif 'keyword' not in list(event.keys()) and 'length' in list(event.keys()):
        response = query_length(event, cursor)
    else:
        response = query_all(cursor)

    return response


def query_keyword(event, cursor):
    records = []
    keyword = event['keyword'].upper()
    query = "SELECT * FROM CPT_Data.cpt WHERE short_description LIKE '%{}%' OR medium_description " \
            "LIKE '%{}%' OR long_description LIKE '%{}%' LIMIT 5".format(keyword, keyword, keyword)
    cursor.execute(query)
    for row in cursor:
        record = {
            'code': row[1],
            'short_description': row[2],
            'medium_description': row[3],
            'long_description': row[4]

        }
        records.append(record)

    return records


def query_length_keyword(event, cursor):
    records = []
    keyword = event['keyword'].upper()
    length = event['length'] + str('_description')
    query = "SELECT cpt_code, {} FROM CPT_Data.cpt WHERE short_description LIKE '%{}%' " \
            "OR medium_description LIKE '%{}%' OR long_description LIKE '%{}%' LIMIT 5".format(length, keyword, keyword, keyword)
    cursor.execute(query)
    for row in cursor:
        record = {
            'code': row[0],
            length: row[1]
        }
        records.append(record)
    return records


def query_length(event, cursor):
    length = event['length'] + str('_description')
    records = []
    query = "SELECT cpt_code, {} FROM CPT_Data.cpt LIMIT 5".format(length)
    cursor.execute(query)
    for row in cursor:
        record = {
            'code': row[0],
            'description': row[1]
        }
        records.append(record)

    return records


def query_all(cursor):
    cursor.execute('SELECT * FROM CPT_Data.cpt LIMIT 10')
    records = []
    for row in cursor:
        record = {
            'cpt_code': row[1],
            'short_description': row[2],
            'medium_description': row[3],
            'long_description': row[4]
        }
        records.append(record)
    return records


