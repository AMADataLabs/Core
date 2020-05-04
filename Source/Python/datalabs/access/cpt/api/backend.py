import psycopg2


connection = psycopg2.connect(
            host='database-test-ui.c3mn4zysffxi.us-east-1.rds.amazonaws.com',
            port=5432,
            user='DataLabs_UI',
            password='hsgdatalabs',
            database='sample')


def lambda_handler(event,context):
    
    cursor = connection.cursor()
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
                    
    return {'statusCode': 200, 'headers' : 'for authorization', 'body' : records}

