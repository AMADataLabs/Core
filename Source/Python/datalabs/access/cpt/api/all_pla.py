import sqlalchemy
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker
from datalabs.etl.cpt.dbmodel import PLACode, PLAShortDescriptor, PLAMediumDescriptor, PLALongDescriptor, Manufacturer, \
    ManufacturerPLACodeMapping, Lab, LabPLACodeMapping, Release
from datalabs.access.database import Database


def lambda_handler(event, context):
    engine = create_engine(Database.url)
    Session = sessionmaker(bind=engine)
    session = Session()

    status_code, response = query_event(event, session)
    return {'statusCode': status_code, 'body': response}


def query_event(event, session):
    query = query_for_code(session)
    query = query_for_release(event.get('since', None), session, query)
    query = query_for_keyword(event.get('keyword', None), event.get('length', None), session, query)

    return get_response_data_from_query(query, event.get('length', None))


def query_for_code(session):
    query = session.query(PLACode, PLALongDescriptor, PLAMediumDescriptor, PLAShortDescriptor).join(PLALongDescriptor,
                                                                                                    PLAMediumDescriptor,
                                                                                                    PLAShortDescriptor,
                                                                                                    Manufacturer, Lab,
                                                                                                    Release)
    return query


def query_for_release(since, session, query):
    if since is not None:
        query = session.query().add_column(Release.publish_date)
        query = query.filter(Release.publish_date.like('%{}%'.format(since)))
        return query
    else:
        return query


def query_for_keyword(keyword, lengths, session, query):
    length_dict = {"long": PLALongDescriptor, "medium": PLAMediumDescriptor, "short": PLAShortDescriptor}
    l = length_dict.get(lengths)

    if keyword is not None:
        if lengths is None:
            query = query.filter(or_((PLALongDescriptor.descriptor.ilike('%{}%'.format(keyword))),
                                     (PLAMediumDescriptor.descriptor.ilike('%{}%'.format(keyword))),
                                     (PLAShortDescriptor.descriptor.ilike('%{}%'.format(keyword)))))

        else:
            query = query.filter(l.descriptor.ilike('%{}%'.format(keyword)))

        return query
    else:
        return query


def get_response_data_from_query(query, lengths):
    if lengths is not None:
        return get_filtered_length_response(query, lengths)
    else:
        return get_content_from_query(query)


def get_filtered_length_response(query, lengths):
    length_dict = {"long": "PLALongDescriptor", "medium": "PLAMediumDescriptor", "short": "PLAShortDescriptor"}
    result = []
    query_exist = query_exists(query)

    if query_exist:
        for row in query.limit(5).all():
            result.append({
                "code": row.Code.code,
                lengths + '_descriptor': getattr(row, length_dict.get(lengths)).descriptor,
                'code_status': row.PLACode.status,
                'effective_date': row.Release.effective_date,
                'lab_name': row.Lab.name,
                'manufacturer_name': row.Manufacturer.name,
                'publish_date': row.Release.publish_date,
                'test_name': row.PLACode.test_name
            })
        return 200, result
    else:
        return 400, {"invalid": "filter"}


def get_content_from_query(query):
    result = []
    query_exist = query_exists(query)

    if query_exist:
        for row in query.limit(5).all():
            record = {
                'code': row.PLACode.code,
                'long_descriptor': row.PLALongDescriptor.descriptor,
                'medium_descriptor': row.PLAMediumDescriptor.descriptor,
                'short_descriptor': row.PLAShortDescriptor.descriptor,
                'code_status': row.PLACode.status,
                'effective_date': row.Release.effective_date,
                'lab_name': row.Lab.name,
                'manufacturer_name': row.Manufacturer.name,
                'publish_date': row.Release.publish_date,
                'test_name': row.PLACode.test_name
            }

            result.append(record)

        return 200, result
    else:
        return 400, {"invalid": "filter"}


def query_exists(query):
    if query.count() == 0:
        return False
    else:
        return True
