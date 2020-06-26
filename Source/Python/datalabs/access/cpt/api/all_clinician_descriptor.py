from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker
from datalabs.etl.cpt.dbmodel import ClinicianDescriptor, ClinicianDescriptorCodeMapping, Release
from datalabs.access.database import Database
import json


def lambda_handler(event, context):
    session = create_database_connection()
    query = query_for_descriptor(session)

    if event.get('multiValueQueryStringParameters', None) is not None:
        query = filter_query_for_release(event, session, query)
        query = filter_query_for_keyword(event, query)

        status_code, response = get_response_data_from_query(query)

    else:
        status_code, response = get_response_data_from_query(query)

    return {
        "statusCode": status_code,
        "body": json.dumps(response)
    }


def create_database_connection():
    engine = create_engine(Database.url)
    Session = sessionmaker(bind=engine)
    return Session()


def query_for_descriptor(session):
    query = session.query(ClinicianDescriptor, ClinicianDescriptorCodeMapping).join(ClinicianDescriptorCodeMapping)
    return query


def filter_query_for_release(event, session, query):
    # needs editing
    if event['multiValueQueryStringParameters'].get('since', None) is not None:
        query = session.query().add_column(Release.publish_date)
        query = query.filter(Release.publish_date.like('%{}%'.format(event)))

    return query


def filter_query_for_keyword(event, query):
    filter_conditions = []

    if event['multiValueQueryStringParameters'].get('keyword', None) is not None:
        for word in event['multiValueQueryStringParameters']['keyword']:
            filter_conditions.append(ClinicianDescriptor.descriptor.ilike('%{}%'.format(word)))

        query = query.filter(or_(*filter_conditions))

    return query


def get_response_data_from_query(query):
    response_rows = []

    for row in query.all():
        response_data = {
            'id': row.ClinicianDescriptor.id,
            'code': row.ClinicianDescriptorCodeMapping.code,
            'descriptor': row.ClinicianDescriptor.descriptor
        }

        response_rows.append(response_data)

    return 200, response_rows
