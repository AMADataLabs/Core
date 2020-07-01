import json
from   sqlalchemy import create_engine
from   sqlalchemy.orm import sessionmaker
from   datalabs.etl.cpt.dbmodel import Release
from   datalabs.access.database import Database


def lambda_handler(event, context):
    session = create_database_connection()
    query = query_for_release(session)

    status_code, response = get_response_from_query(query, event.get('queryStringParameters', None))

    return {
        "statusCode": status_code,
        "body": json.dumps(response)
    }


def create_database_connection():
    engine = create_engine(Database.url)
    Session = sessionmaker(bind=engine)
    return Session()


def query_for_release(session):
    query = session.query(Release)
    return query


def get_response_from_query(query, query_parameter):
    status_code = 200

    if query_parameter is not None:
        results = query_parameter['results']

        if results.isdigit():
            query = query.limit(results).all()
            response_data = get_content_from_rows(query)
        else:
            response_data = 'Invalid query parameter'
            status_code = 400

    else:
        query = query.all()
        response_data = get_content_from_rows(query)

    return status_code, response_data


def get_content_from_rows(query):
    response_rows = []

    for row in query:
        response_data = {
            'id': row.id,
            'publish_date': str(row.publish_date),
            'effective_date': str(row.effective_date),
            'type': row.type
        }

        response_rows.append(response_data)

    return response_rows
