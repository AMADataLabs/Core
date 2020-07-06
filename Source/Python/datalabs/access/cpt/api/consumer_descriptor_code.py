import json
from   sqlalchemy import create_engine
from   sqlalchemy.orm import sessionmaker
from   datalabs.etl.cpt.dbmodel import ConsumerDescriptor
from   datalabs.access.database import Database


def lambda_handler(event, context):
    session = create_database_connection()
    query = query_for_descriptor(session, event.get('pathParameters', None))

    status_code, response = get_content_from_query_output(query)

    return {'statusCode': status_code, 'body': json.dumps(response[0])}


def create_database_connection():
    engine = create_engine(Database.url)
    Session = sessionmaker(bind=engine)
    return Session()


def query_for_descriptor(session, path_parameter):
    query = None

    if path_parameter is not None:
        query = session.query(ConsumerDescriptor)
        query = query.filter(ConsumerDescriptor.code == path_parameter['code'])

    return query


def get_content_from_query_output(query):
    if query is not None and query.count() != 0:
        rows = [dict(code=row.code, descriptor=row.descriptor) for row in query.all()]
        status_code = 200

    else:
        status_code = 404
        rows = ['No Consumer Descriptor found for the given CPT code.']

    return status_code, rows
