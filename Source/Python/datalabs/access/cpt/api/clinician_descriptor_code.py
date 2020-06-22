from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datalabs.etl.cpt.dbmodel import ClinicianDescriptorCodeMapping, ClinicianDescriptor
from datalabs.access.database import Database
import json


def lambda_handler(event, context):
    session = create_database_connection()

    query = query_for_descriptor(session)
    query = query_by_code(query, event)
    status_code, response = get_content_from_query_output(query)

    return {
        'statusCode': status_code,
        'body': json.dumps(response)
    }


def create_database_connection():
    engine = create_engine(Database.url)
    Session = sessionmaker(bind=engine)
    return Session()


def query_for_descriptor(session):
    query = session.query(ClinicianDescriptor, ClinicianDescriptorCodeMapping).join(ClinicianDescriptorCodeMapping)
    return query


def query_by_code(query, event):
    if event.get('pathParameters', None) is not None:
        query = query.filter(ClinicianDescriptorCodeMapping.code == event['pathParameters']['code'])

    else:
        query = None

    return query


def get_content_from_query_output(query):
    if query is not None:
        rows = []
        for row in query.all():
            record = {
                'id': row.ClinicianDescriptor.id,
                'code': row.ClinicianDescriptorCodeMapping.code,
                'description': row.ClinicianDescriptor.descriptor
            }
            rows.append(record)
        status_code = 200

    else:
        status_code = 400
        rows = {"Code": "No given"}

    return status_code, rows
