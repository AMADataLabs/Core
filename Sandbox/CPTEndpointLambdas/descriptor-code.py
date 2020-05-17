import psycopg2

CONNECTION = psycopg2.connect(
    host='database-test-ui.c3mn4zysffxi.us-east-1.rds.amazonaws.com',
    port=5432,
    user='DataLabs_UI',
    password='hsgdatalabs',
    database='sample')

CURSOR = CONNECTION.cursor()


def lambda_handler(event, context):
    requested_id = str(event['id'])
    query = "SELECT * FROM CPT_Data.clinician_descriptor WHERE concept_id='{}'".format(requested_id)
    CURSOR.execute(query)
    records = []
    for row in CURSOR:
        record = {
            'concept_id': row[1],
            'cpt_code': row[2],
            'clinician_descriptor_id': row[3],
            'clinical_descriptor': row[4]

        }
        records.append(record)

    return {'statusCode': 200, 'headers': 'auth', 'body': records}







