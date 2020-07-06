import json
from   sqlalchemy import create_engine, or_
from   sqlalchemy.orm import sessionmaker
from   datalabs.etl.cpt.dbmodel import ConsumerDescriptor, Release
from   datalabs.access.database import Database


def lambda_handler(event, context):
    query_parameter = event.get('multiValueQueryStringParameters', None)

    session = create_database_connection()
    query = query_for_descriptors(session)

    if query_parameter is not None:
        query = filter_query_for_release(query_parameter.get('since', None), query)
        query = filter_query_for_keywords(query_parameter.get('keyword', None), query)

    status_code, response = get_response_data_from_query(query)

    return {
        "statusCode": status_code,
        "body": json.dumps(response)
    }


def create_database_connection():
    engine = create_engine(Database.url)
    Session = sessionmaker(bind=engine)
    return Session()


def query_for_descriptors(session):
    query = session.query(ConsumerDescriptor)
    return query


def filter_query_for_release(since, query):
    if since is not None:
        query = query.add_column(Release.effective_date)
        query = query.filter(Release.effective_date >= since)

    return query


def filter_query_for_keywords(keyword, query):
    if keyword is not None:
        filter_conditions = [(ConsumerDescriptor.descriptor.ilike('%{}%'.format(word))) for word in keyword]
        query = query.filter(or_(*filter_conditions))

    return query


def get_response_data_from_query(query):
    response_rows = [dict(code=row.code, descriptor=row.descriptor) for row in query.all()]

    return 200, response_rows
