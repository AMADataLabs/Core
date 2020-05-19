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
    code_exists = check_code(event)
    if code_exists:
        filter_exists = check_event(event)
        if filter_exists:
            response = query_length(event, cursor)
        else:
            response = query_all(event, cursor)

        return 200, response
    else:
        return 400, {"Error": "No Code Given"}


def check_code(event):
    requested_code = event['code']
    if requested_code is None:
        return False
    else:
        return True


def check_event(event):
    if 'length' in list(event.keys()):
        return True
    else:
        return False


def query_length(event, cursor):
    length_exists = check_length(event)
    if length_exists:
        length = event['length'] + str('_description')
        requested_code = event['code']
        query = "SELECT cpt_code, {} FROM CPT_Data.cpt WHERE cpt_code= '{}'".format(length, requested_code)
        print('test')
        cursor.execute(query)
        for row in cursor:
            record = {
                'cpt_code': row[0],
                length: row[1]

            }
        return 200, record
    else:
        return 400, {event['length']: "Invalid"}


def query_all(event, cursor):
    requested_id = event['code']
    query = "SELECT * FROM CPT_Data.cpt WHERE cpt_code= '{}'".format(requested_id)
    cursor.execute(query)
    if cursor.rowcount == 0:
        return 400, {requested_id: "Does Not Exist"}
    else:
        for row in cursor:
            record = {
                'cpt_code': row[1],
                'short_description': row[2],
                'medium_description': row[3],
                'long_description': row[4]

            }
    return 200, record


def check_length(event):
    given_length = event['length'].lower()
    if given_length == 'short' or given_length == 'medium' or given_length == 'long':
        return True
    else:
        return False
