from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datalabs.etl.cpt.dbmodel import ClinicianDescriptorCodeMapping, ClinicianDescriptor
from datalabs.access.database import Database


def lambda_handler(event, context):
    engine = create_engine(Database.url)
    Session = sessionmaker(bind=engine)
    session = Session()

    status_code, response = query_event(event, session)

    return {'statusCode': status_code, 'body': response}


def query_event(event, session):
    if code_is_not_null(event):
        return query_by_code(event, session)
    else:
        return 400, {"Error": "No code given"}


def code_is_not_null(event):
    code = event.get('code', None)
    if code is not None:
        return True
    else:
        return False


def query_by_code(event, session):
    requested_code = event['code']
    result = session.query(ClinicianDescriptorCodeMapping, ClinicianDescriptor).join(ClinicianDescriptor) \
        .filter(ClinicianDescriptorCodeMapping.code == '{}'.format(requested_code))

    if result.count() != 0:
        return get_content_from_query_output(result)
    else:
        return 400, {'code': 'bad'}


def get_content_from_query_output(result):
    rows = []
    for row in result:
        record = {
            'id': row.ClinicianDescriptor.id,
            'code': row.ClinicianDescriptorCodeMapping.code,
            'description': row.ClinicianDescriptor.descriptor
        }
        rows.append(record)
    return 200, rows
