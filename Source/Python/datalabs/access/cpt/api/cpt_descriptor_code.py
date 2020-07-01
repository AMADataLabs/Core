from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datalabs.etl.cpt.dbmodel import Code, ShortDescriptor, LongDescriptor, MediumDescriptor
from datalabs.access.database import Database
import json


def lambda_handler(event, context):
    path_parameter = event.get('pathParameters', None)

    session = create_database_connection()
    query = query_for_descriptor(session, path_parameter)

    status_code, response = get_response_data_from_query(query, path_parameter.get('lengths', None))

    return {'statusCode': status_code, 'body': json.dumps(response[0])}


def create_database_connection():
    engine = create_engine(Database.url)
    Session = sessionmaker(bind=engine)
    return Session()


def query_for_descriptor(session, path_parameter):
    query = None

    if path_parameter is not None:
        query = session.query(Code, LongDescriptor, MediumDescriptor, ShortDescriptor).join(LongDescriptor,
                                                                                            MediumDescriptor,
                                                                                            ShortDescriptor)
        query = query.filter(Code.code == path_parameter['code'])

    return query


def get_response_data_from_query(query, lengths):
    if lengths is not None:
        if lengths_exist(lengths):
            status_code, response_data = get_filtered_length_response(query, lengths)
        else:
            status_code = 400
            response_data = 'Invalid query parameter'
    else:
        status_code, response_data = get_content_from_query(query)

    return status_code, response_data


def lengths_exist(lengths):
    length_dict = {"long": LongDescriptor, "medium": MediumDescriptor, "short": ShortDescriptor}
    return all([length in lengths for length in length_dict.keys()])


def get_filtered_length_response(query, lengths):
    response_data = []
    length_dict = {"long": 'LongDescriptor', "medium": 'MediumDescriptor', "short": 'ShortDescriptor'}

    if query is not None:
        for row in query.all():
            response_row = {"code": row.Code.code}
            for length in lengths:
                response_row.update({length + '_descriptor': getattr(row, length_dict.get(length)).descriptor})

            response_data.append(response_row)
        status_code = 200

    else:
        response_data = 'No descriptor found for the given CPT Code'
        status_code = 404

    return status_code, response_data


def get_content_from_query(query):

    if query is not None:
        response_row = [dict(
            code=row.Code.code,
            long_descriptor=row.LongDescriptor.descriptor,
            medium_descriptor=row.MediumDescriptor.descriptor,
            short_descriptor=row.ShortDescriptor.descriptor,) for row in query.all()]
        status_code = 200
    else:
        response_row = {'code': 'invalid'}
        status_code = 404

    return status_code, response_row
