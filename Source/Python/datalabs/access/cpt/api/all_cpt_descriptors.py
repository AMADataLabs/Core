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

    status_code, response = query_event(event, cursor)
    return {'statusCode': status_code, 'body': response}


def query_event(event, cursor):
    print("hi")
    event_type = check_event(event)
    if event_type == 'keyword':
        status, body = query_keyword(event, cursor)
        return status, body
    elif event_type == 'length':
        status, body = query_length(event, cursor)
        return status, body
    elif event_type == 'since':
        status, body = query_since(event, cursor)
        return status, body
    elif event_type == 'length_and_keyword':
        status, body = query_length_keyword(event, cursor)
        return status, body
    elif event_type == 'length_since':
        status, body = query_length_since(event, cursor)
        return status, body
    elif event_type == 'keyword_since':
        status, body = query_keyword_since(event, cursor)
        return status, body
    else:
        status, body = query_all(cursor)
        return status, body


def check_event(event):
    if 'keyword' in list(event.keys()) and 'length' not in list(event.keys()) and 'since' not in list(event.keys()):
        response = 'keyword'
    elif 'keyword' not in list(event.keys()) and 'length' in list(event.keys()) and 'since' not in list(event.keys()):
        response = 'length'
    elif 'keyword' not in list(event.keys()) and 'length' not in list(event.keys()) and 'since' in list(event.keys()):
        response = 'since'
    elif 'keyword' in list(event.keys()) and 'length' in list(event.keys()) and 'since' not in list(event.keys()):
        response = 'length_keyword'
    elif 'keyword' not in list(event.keys()) and 'length' in list(event.keys()) and 'since' in list(event.keys()):
        response = 'length_since'
    elif 'keyword' in list(event.keys()) and 'length' in list(event.keys()) and 'since' in list(event.keys()):
        response = 'keyword_since'
    else:
        response = 'no_filters'

    return response


def query_keyword(event, cursor):
    all_rows = []
    keyword = event['keyword'].upper()
    query = "SELECT * FROM CPT_Data.cpt WHERE short_description LIKE '%{}%' OR medium_description " \
            "LIKE '%{}%' OR long_description LIKE '%{}%' LIMIT 5".format(keyword, keyword, keyword)
    cursor.execute(query)
    if cursor.rowcount == 0:
        return 400, {event['keyword']: "Not Found"}
    else:
        for row in cursor:
            record = {
                'code': row[1],
                'short_description': row[2],
                'medium_description': row[3],
                'long_description': row[4]

            }
            all_rows.append(record)
        return 200, all_rows


def query_length(event, cursor):
    length_exists = check_if_length_exists(event)
    if length_exists:
        length = event['length'] + str('_description')
        all_rows = []
        query = "SELECT cpt_code, {} FROM CPT_Data.cpt LIMIT 5".format(length)
        cursor.execute(query)
        for row in cursor:
            record = {
                'code': row[0],
                'description': row[1]
            }
            all_rows.append(record)

        return 200, all_rows
    else:
        return 400, {event['length']: "Invalid"}


def query_since(event, cursor):
    return 200, {"In": "Progress"}


def query_length_keyword(event, cursor):
    all_rows = []
    keyword = event['keyword'].upper()
    length = event['length'] + str('_description')
    query = "SELECT cpt_code, {} FROM CPT_Data.cpt WHERE short_description LIKE '%{}%' " \
            "OR medium_description LIKE '%{}%' OR long_description LIKE '%{}%' LIMIT 5".format(length, keyword, keyword,
                                                                                               keyword)
    length_exists = check_if_length_exists(event)

    if not length_exists:
        return 400, {"Invalid": "Length"}
    elif length_exists:
        if cursor.execute(query) == 0:
            return 400, {"Invalid": "Keyword"}
        else:
            for row in cursor:
                record = {
                    'code': row[0],
                    length: row[1]
                }
                all_rows.append(record)
            return 200, all_rows


def query_length_since(event, cursor):
    return 200, {"In": "Progress"}


def query_keyword_since(event, cursor):
    return 200, {"In": "Progress"}


def query_all(cursor):
    cursor.execute('SELECT * FROM CPT_Data.cpt LIMIT 10')
    all_rows = []
    for row in cursor:
        record = {
            'cpt_code': row[1],
            'short_description': row[2],
            'medium_description': row[3],
            'long_description': row[4]
        }
        all_rows.append(record)
    return 200, all_rows


def check_if_length_exists(event):
    given_length = event['length'].lower()
    if given_length == 'short' or given_length == 'medium' or given_length == 'long':
        return True
    else:
        return False
