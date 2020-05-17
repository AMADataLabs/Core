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
    if 'keyword' in list(event.keys()):
        response = query_keyword(event)

    elif "since" in list(event.keys()):
        response = query_date(event)

    else:
        response = query_all(event)

    return response


def query_all(event):
    CURSOR.execute('SELECT * FROM CPT_Data.clinician_descriptor LIMIT 10')
    records = []
    for row in CURSOR:
        record = {
            'concept_id': row[1],
            'cpt_code': row[2],
            'clinician_descriptor_id': row[3],
            'clinical_descriptor': row[4]

        }
        records.append(record)

    return records


def query_keyword(event):
    records = []
    keyword = event['keyword'].upper()
    query = "SELECT * FROM CPT_Data.clinician_descriptor WHERE clinical_descriptor LIKE '%{}%'".format(keyword)
    CURSOR.execute(query)
    for row in CURSOR:
        record = {
            'concept_id': row[1],
            'cpt_code': row[2],
            'clinician_descriptor_id': row[3],
            'clinical_descriptor': row[4]

        }

        records.append(record)
    return records


def query_date(date):
    return 'test'