from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker
from datalabs.etl.cpt.dbmodel import Code, ShortDescriptor, LongDescriptor, MediumDescriptor, Release
from datalabs.access.database import Database
import json


def lambda_handler(event, context):
    session = create_database_connection()
    query = query_for_code(session)

    if event.get('multiValueQueryStringParameters', None) is not None:
        query = filter_query_for_release(event, session, query)
        query = filter_query_for_keyword(event, query)

        status_code, response = get_response_data_from_query(query, event)

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


def query_for_code(session):
    query = session.query(Code, LongDescriptor, MediumDescriptor, ShortDescriptor).join(LongDescriptor,
                                                                                        MediumDescriptor,
                                                                                        ShortDescriptor)
    return query


def filter_query_for_release(event, session, query):
    # needs editing
    if event['multiValueQueryStringParameters'].get('since', None) is not None:
        query = session.query().add_column(Release.publish_date)
        query = query.filter(Release.publish_date.like('%{}%'.format(event)))

    return query


def filter_query_for_keyword(event, query):
    filter_conditions = []

    if event['multiValueQueryStringParameters'].get('keyword', None) is not None and \
            event['multiValueQueryStringParameters'].get('length', None) is None:

        for word in event['multiValueQueryStringParameters']['keyword']:
            filter_conditions.append(LongDescriptor.descriptor.ilike('%{}%'.format(word)))
            filter_conditions.append(MediumDescriptor.descriptor.like('%{}%'.format(word)))
            filter_conditions.append(ShortDescriptor.descriptor.like('%{}%'.format(word)))

        query = query.filter(or_(*filter_conditions))

    elif event['multiValueQueryStringParameters'].get('keyword', None) is not None:
        query = filter_query_for_keyword_with_length(query, event["multiValueQueryStringParameters"]['length'],
                                                     event["multiValueQueryStringParameters"]['keyword'])

    return query


def filter_query_for_keyword_with_length(query, lengths, keyword):
    length_dict = {"long": LongDescriptor, "medium": MediumDescriptor, "short": ShortDescriptor}
    filter_conditions = []

    if lengths_exist(lengths, length_dict):
        for length in lengths:
            for word in keyword:
                filter_conditions.append((length_dict.get(length).descriptor.ilike('%{}%'.format(word))))

        query = query.filter(or_(*filter_conditions))
    else:
        query = None

    return query


def lengths_exist(lengths, length_dict):
    for length in lengths:
        if length in list(length_dict.keys()):
            condition = True
        else:
            condition = False
            break

    return condition


def get_response_data_from_query(query, event):
    length_dict = {"long": LongDescriptor, "medium": MediumDescriptor, "short": ShortDescriptor}
    lengths = event["multiValueQueryStringParameters"].get('length', None)

    if lengths is not None:
        if lengths_exist(lengths, length_dict):
            response_data = get_filtered_length_response(query, lengths)
            status_code = 200
        else:
            status_code = 400
            response_data = {'length(s)': 'invalid'}
    else:
        response_data = get_content_from_query(query)
        status_code = 200

    return status_code, response_data


def get_filtered_length_response(query, lengths):
    response_rows = []
    length_dict = {"long": 'LongDescriptor', "medium": 'MediumDescriptor', "short": 'ShortDescriptor'}

    for row in query.all():
        response_data = {"code": row.Code.code}
        for length in lengths:
            length = {length + '_descriptor': getattr(row, length_dict.get(length)).descriptor}
            response_data.update(length)

        response_rows.append(response_data)

    return response_rows


def get_content_from_query(query):
    response_rows = []

    for row in query.all():
        response_data = {
            'code': row.Code.code,
            'long_descriptor': row.LongDescriptor.descriptor,
            'medium_descriptor': row.MediumDescriptor.descriptor,
            'short_descriptor': row.ShortDescriptor.descriptor
        }

        response_rows.append(response_data)

    return response_rows
