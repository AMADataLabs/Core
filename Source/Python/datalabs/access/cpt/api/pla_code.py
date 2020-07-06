import sqlalchemy
import json
from   sqlalchemy import create_engine, or_
from   sqlalchemy.orm import sessionmaker
from   datalabs.etl.cpt.dbmodel import PLACode, PLAShortDescriptor, PLAMediumDescriptor, PLALongDescriptor, Manufacturer, \
    ManufacturerPLACodeMapping, Lab, LabPLACodeMapping, Release
from   datalabs.access.database import Database


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
        query = session.query(PLACode, PLALongDescriptor, PLAMediumDescriptor, PLAShortDescriptor).join(
            PLALongDescriptor,
            PLAMediumDescriptor,
            PLAShortDescriptor,
            Manufacturer, Lab,
            Release)
        query = query.filter(PLACode.code == path_parameter['code'])

    return query


def get_response_data_from_query(query, lengths):
    if lengths is not None:
        if lengths_exist(lengths):
            status_code, response_data = get_filtered_length_response(query, lengths)
        else:
            status_code = 400
            response_data = ['invalid query parameter']
    else:
        status_code, response_data = get_content_from_query(query)

    return status_code, response_data


def lengths_exist(lengths):
    length_dict = {"long": PLALongDescriptor, "medium": PLAMediumDescriptor, "short": PLAShortDescriptor}
    return all([length in lengths for length in length_dict.keys()])


def get_filtered_length_response(query, lengths):
    length_dict = {"long": "PLALongDescriptor", "medium": "PLAMediumDescriptor", "short": "PLAShortDescriptor"}
    response_rows = []

    if query is not None:
        for row in query.all():
            response_data = {'code': row.PLACode.code,
                             'code_status': row.PLACode.status,
                             'effective_date': row.Release.effective_date,
                             'lab_name': row.Lab.name,
                             'manufacturer_name': row.Manufacturer.name,
                             'publish_date': row.Release.publish_date,
                             'test_name': row.PLACode.test_name}
            for length in lengths:
                length = {length + '_descriptor': getattr(row, length_dict.get(length)).descriptor}
                response_data.update(length)

            response_rows.append(response_data)
        status_code = 200

    else:
        response_rows = ['No PLA details found for the given PLA code']
        status_code = 404

    return status_code, response_rows


def get_content_from_query(query):
    if query is not None:
        rows = [dict(
            code=row.PLACode.code,
            long_descriptor=row.PLALongDescriptor.descriptor,
            medium_descriptor=row.PLAMediumDescriptor.descriptor,
            short_descriptor=row.PLAShortDescriptor.descriptor,
            code_status=row.PLACode.status,
            effective_date=row.Release.effective_date,
            lab_name=row.Lab.name,
            manufacturer_name=row.Manufacturer.name,
            publish_date=row.Release.publish_date,
            test_name=row.PLACode.test_name) for row in query.all()]
        status_code = 200

    else:
        rows = ['No PLA details found for the given PLA code']
        status_code = 404

    return status_code, rows
