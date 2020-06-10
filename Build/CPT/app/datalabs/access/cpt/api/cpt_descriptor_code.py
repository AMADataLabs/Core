from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datalabs.etl.cpt.dbmodel import Code, ShortDescriptor, LongDescriptor, MediumDescriptor
from datalabs.access.database import Database


def lambda_handler(event, context):
    engine = create_engine(Database.url)
    Session = sessionmaker(bind=engine)
    session = Session()

    status_code, response = query_event(event, session)
    return {'statusCode': status_code, 'body': response}


def query_event(event, session):
    if code_is_not_null(event):
        return query_all(event, session)
    else:
        return 400, {"Error": "No code given"}


def code_is_not_null(event):
    code = event.get('code', None)
    if code is not None:
        return True
    else:
        return False


def query_all(event, session):
    requested_code = event['code']
    query = session.query(Code, LongDescriptor, ShortDescriptor, MediumDescriptor).join(ShortDescriptor, LongDescriptor,
                                                                                        MediumDescriptor).filter(
        Code.code == '{}'.format(requested_code))

    if query.count() == 0:
        return 400, {'code': 'bad'}
    else:
        return filter_code(query, event)


def filter_code(query, event):
    requested_filter = event.get('length', None)

    if requested_filter != None:
        return get_filtered_content_from_query(query, requested_filter)
    else:
        return get_content_from_query(query)


def get_content_from_query(query):
    record = {}

    for row in query:
        record = {
            'code': row.Code.code,
            'long_descriptor': row.LongDescriptor.descriptor,
            'medium_descriptor': row.MediumDescriptor.descriptor,
            'short_descriptor': row.ShortDescriptor.descriptor
        }

    return 200, record


def get_filtered_content_from_query(query, lengths):
    length_dict = {"long": 'LongDescriptor', "medium": 'MediumDescriptor', "short": 'ShortDescriptor'}
    record = {}

    for row in query:
        record.update({'code': row.Code.code})
        for length in lengths:
            length = length_dict.get(length)
            record.update({length: getattr(row, length).descriptor})

    return 200, record
