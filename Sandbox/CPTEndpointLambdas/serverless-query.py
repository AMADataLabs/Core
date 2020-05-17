import json
import psycopg2

CONNECTION = psycopg2.connect(
    host='database-test-ui.c3mn4zysffxi.us-east-1.rds.amazonaws.com',
    port=5432,
    user='DataLabs_UI',
    password='hsgdatalabs',
    database='sample')
CURSOR = CONNECTION.cursor()


def lambda_handler(event, context):
    response = check_event(event)

    return {'statusCode': 200, 'body': response}


def check_event(event):
    if 'keyword' in list(event.keys()) and 'length' in list(event.keys()):
        response = query_length_keyword(event)
    elif 'keyword' in list(event.keys()) and 'length' not in list(event.keys()):
        response = query_keyword(event)
    elif 'keyword' not in list(event.keys()) and 'length' in list(event.keys()):
        response = query_length(event)

    return response


def query_all():
    CURSOR.execute('SELECT * FROM CPT_Data.cpt LIMIT 10')
    records = []
    for row in CURSOR:
        record = {
            'cpt_code': row[1],
            'short_description': row[2],
            'medium_description': row[3],
            'long_description': row[4]
        }
        records.append(record)
    return records


def query_length(event):
    length = event['length'] + str('_description')
    records = []
    query = "SELECT cpt_code, {} FROM CPT_Data.cpt LIMIT 5".format(length)
    CURSOR.execute(query)
    for row in CURSOR:
        record = {
            'code': row[0],
            'description': row[1]
        }
        records.append(record)

    return records


def query_keyword(event):
    records = []
    keyword = event['keyword'].upper()
    query = "SELECT * FROM CPT_Data.cpt WHERE short_description LIKE '%{}%' OR medium_description " \
            "LIKE '%{}%' OR long_description LIKE '%{}%' LIMIT 5".format(keyword, keyword, keyword)
    CURSOR.execute(query)
    for row in CURSOR:
        record = {
            'code': row[1],
            'short_description': row[2],
            'medium_description': row[3],
            'long_description': row[4]

        }
        records.append(record)

    return records


def query_length_keyword(event):
    records = []
    keyword = event['keyword'].upper()
    length = event['length'] + str('_description')
    query = "SELECT cpt_code, {} FROM CPT_Data.cpt WHERE short_description LIKE '%{}%' OR medium_description" \
            " LIKE '%{}%' OR long_description LIKE '%{}%' LIMIT 5".format(length, keyword, keyword, keyword)
    CURSOR.execute(query)
    for row in CURSOR:
        record = {
            'code': row[0],
            length: row[1]
        }
        records.append(record)
    return records
