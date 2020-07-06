import json
from   sqlalchemy import create_engine
from   sqlalchemy.orm import sessionmaker
from   datalabs.etl.cpt.dbmodel import ClinicianDescriptorCodeMapping, ClinicianDescriptor
from   datalabs.access.database import Database


def lambda_handler(event, context):
    session = create_database_connection()
    query = query_for_descriptor(session, event.get('pathParameters', None))

    status_code, response = get_content_from_query_output(query)

    return {'statusCode': status_code, 'body': json.dumps(response)}


def create_database_connection():
    engine = create_engine(Database.url)
    Session = sessionmaker(bind=engine)
    return Session()


def query_for_descriptor(session, path_parameter):
    query = None

    if path_parameter is not None:
        query = session.query(ClinicianDescriptor, ClinicianDescriptorCodeMapping).join(ClinicianDescriptorCodeMapping)
        query = query.filter(ClinicianDescriptorCodeMapping.code == path_parameter['code'])

    return query


def get_content_from_query_output(query):
    if query is not None:
        rows = [dict(id=row.ClinicianDescriptor.id,
                     code=row.ClinicianDescriptorCodeMapping.code,
                     description=row.ClinicianDescriptor.descriptor) for row in query.all()]
        status_code = 200

    else:
        status_code = 404
        rows = 'No descriptor found for the given CPT Code'

    return status_code, rows
