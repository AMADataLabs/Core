import json
from   sqlalchemy import create_engine, or_
from   sqlalchemy.orm import sessionmaker
from   datalabs.etl.cpt.dbmodel import Code, ShortDescriptor, LongDescriptor, MediumDescriptor, Release
from   datalabs.access.database import Database


def lambda_handler(event, context):
    query_parameter = event.get('multiValueQueryStringParameters', None)

    session = create_database_connection()
    query = query_for_code(session)

    if query_parameter is not None:
        query = filter_query_for_release(query_parameter.get('since', None), query_parameter, query)
        query = filter_query_for_keywords(query_parameter.get('keyword', None),
                                          query_parameter, query_parameter.get('length', None), query)

        status_code, response = get_response_data_from_query(query, query_parameter.get('length', None))

    else:
        status_code, response = get_content_from_query(query)

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


def filter_query_for_release(since, query_parameter, query):
    if since is not None:
        query = query.add_column(Release.effective_date)
        for date in query_parameter['since']:
            query = query.filter(Release.effective_date >= date)

    return query


def filter_query_for_keywords(keyword, query_parameter, length, query):
    filter_conditions = []

    if keyword is not None and length is None:

        for word in query_parameter['keyword']:
            filter_conditions.append(LongDescriptor.descriptor.ilike('%{}%'.format(word)))
            filter_conditions.append(MediumDescriptor.descriptor.like('%{}%'.format(word)))
            filter_conditions.append(ShortDescriptor.descriptor.like('%{}%'.format(word)))

        query = query.filter(or_(*filter_conditions))

    elif keyword is not None:
        query = filter_query_for_keyword_with_length(query, query_parameter['length'], query_parameter['keyword'])

    return query


def filter_query_for_keyword_with_length(query, lengths, keyword):
    length_dict = {"long": LongDescriptor, "medium": MediumDescriptor, "short": ShortDescriptor}
    filter_conditions = []

    if lengths_exist(lengths, length_dict):
        for length in lengths:
            filter_conditions = [(length_dict.get(length).descriptor.ilike('%{}%'.format(word))) for word in keyword]
        query = query.filter(or_(*filter_conditions))
    else:
        query = None

    return query


def lengths_exist(lengths, length_dict):
    return all([length in lengths for length in length_dict.keys()])


def get_response_data_from_query(query, lengths):
    length_dict = {"long": LongDescriptor, "medium": MediumDescriptor, "short": ShortDescriptor}

    if lengths is not None:
        if lengths_exist(lengths, length_dict):
            response_data = get_filtered_length_content(query, lengths)
            status_code = 200
        else:
            status_code = 400
            response_data = 'Invalid query parameter'
    else:
        response_data = get_content_from_query(query)
        status_code = 200

    return status_code, response_data


def get_filtered_length_content(query, lengths):
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
    response_rows = [
        dict(
            code=row.Code.code,
            long_descriptor=row.LongDescriptor.descriptor,
            medium_descriptor=row.MediumDescriptor.descriptor,
            short_descriptor=row.ShortDescriptor.descriptor, )
        for row in query.all()
    ]

    return response_rows
