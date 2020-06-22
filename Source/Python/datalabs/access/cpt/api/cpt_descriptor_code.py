from   sqlalchemy import create_engine
from   sqlalchemy.orm import sessionmaker
from   datalabs.etl.cpt.dbmodel import Code, ShortDescriptor, LongDescriptor, MediumDescriptor
from   datalabs.access.database import Database
import json


def lambda_handler(event, context):
    session = create_database_connection()

    query = query_for_descriptor(session)
    query = query_by_code(query, event)

    if event.get('multiValueQueryStringParameters', None) is not None:
        status_code, response = get_filtered_length_response(query, event['multiValueQueryStringParameters']['length'])
    else:
        response = get_content_from_query(query)
        status_code = 200

    return {
        "statusCode": status_code,
        "body": json.dumps(response)
    }


def create_database_connection():
    engine = create_engine(Database.url)
    Session = sessionmaker(bind=engine)
    return Session()


def query_for_descriptor(session):
    query = session.query(Code, LongDescriptor, MediumDescriptor, ShortDescriptor).join(LongDescriptor,
                                                                                        MediumDescriptor,
                                                                                        ShortDescriptor)
    return query


def query_by_code(query, event):
    if event.get('pathParameters', None) is not None:
        query = query.filter(Code.code == event['pathParameters']['code'])

    else:
        query = None

    return query


def get_response_data_from_query(query, event):
    lengths = event["multiValueQueryStringParameters"].get('length', None)

    if lengths is not None:
        if lengths_exist(lengths):
            response_data = get_filtered_length_response(query, lengths)
            status_code = 200
        else:
            status_code = 400
            response_data = {'length(s)': 'invalid'}
    else:
        response_data = get_content_from_query(query)
        status_code = 200

    return status_code, response_data


def lengths_exist(lengths):
    length_dict = {"long": LongDescriptor, "medium": MediumDescriptor, "short": ShortDescriptor}

    for length in lengths:
        if length in list(length_dict.keys()):
            condition = True
        else:
            condition = False
            break

    return condition


def get_filtered_length_response(query, lengths):
    response_data = []
    length_dict = {"long": 'LongDescriptor', "medium": 'MediumDescriptor', "short": 'ShortDescriptor'}

    if query is not None:
        for row in query.all():
            response_row = {"code": row.Code.code}
            for length in lengths:
                response_row.update({length + '_descriptor': getattr(row, length_dict.get(length)).descriptor})

            response_data.append(response_row)
    else:
        response_data = {'code': 'not given'}

    return response_data


def get_content_from_query(query):
    response_row = []
    print(query)
    if query is not None:
        for row in query.all():
            response_data = {
                'code': row.Code.code,
                'long_descriptor': row.LongDescriptor.descriptor,
                'medium_descriptor': row.MediumDescriptor.descriptor,
                'short_descriptor': row.ShortDescriptor.descriptor
            }
            response_row.append(response_data)
    else:
        response_row = {'code': 'not given'}

    return response_row


