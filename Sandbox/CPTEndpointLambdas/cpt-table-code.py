import psycopg2

connection = psycopg2.connect(
    host='database-test-ui.c3mn4zysffxi.us-east-1.rds.amazonaws.com',
    port=5432,
    user='DataLabs_UI',
    password='hsgdatalabs',
    database='sample')

CURSOR = connection.cursor()


def lambda_handler(event, context):
    response = check_event(event)

    return {'statusCode': 200, 'body': response}


def check_event(event):
    if 'length' in list(event.keys()):
        response = query_length(event)
    else:
        response = query_all(event)
    return response


def query_length(event):
    length = event['length'] + str('_description')
    requested_id = event['code']
    query = "SELECT cpt_code, {} FROM CPT_Data.cpt WHERE cpt_code= {}".format(length, requested_id)
    CURSOR.execute(query)
    for row in CURSOR:
        record = {
            'cpt_code': row[0],
            length: row[1]

        }
    return record


def query_all(event):
    requested_id = event['code']
    query = "SELECT * FROM CPT_Data.cpt WHERE cpt_code= '{}'".format(requested_id)
    CURSOR.execute(query)
    for row in CURSOR:
        record = {
            'cpt_code': row[1],
            'short_description': row[2],
            'medium_description': row[3],
            'long_description': row[4]

        }
    return record