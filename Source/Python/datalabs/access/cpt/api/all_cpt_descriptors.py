from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker
from datalabs.etl.cpt.dbmodel import Code, ShortDescriptor, LongDescriptor, MediumDescriptor, Release
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

    return get_response_data_from_query(query, event.get('length', None), session)


def query_for_code(session):
    query = session.query(Code, LongDescriptor, MediumDescriptor, ShortDescriptor).join(LongDescriptor,
                                                                                        MediumDescriptor,
                                                                                        ShortDescriptor)
    return query


def query_for_release(since, session, query):
    if since is not None:
        query = session.query().add_column(Release.publish_date)
        print(query)
        query = query.filter(Release.publish_date.like('%{}%'.format(since)))
        return query
    else:
        return query


def query_for_keyword(keyword, lengths, session, query):
    length_dict = {"long": LongDescriptor, "medium": MediumDescriptor, "short": ShortDescriptor}
    l = length_dict.get(lengths)

    if keyword is not None:
        if lengths is None:
            query = query.filter(or_((LongDescriptor.descriptor.ilike('%{}%'.format(keyword))),
                                     (MediumDescriptor.descriptor.like('%{}%'.format(keyword))),
                                     (ShortDescriptor.descriptor.like('%{}%'.format(keyword)))))

        else:
            query = query.filter(l.descriptor.ilike('%{}%'.format(keyword)))

        return query
    else:
        return query


def get_response_data_from_query(query, lengths, session):
    print(query)
    if lengths is not None:
        return get_filtered_length_response(query, lengths)
    else:
        return get_content_from_query(query)


def get_filtered_length_response(query, lengths):
    length_dict = {"long": "LongDescriptor", "medium": "MediumDescriptor", "short": "ShortDescriptor"}
    result = []
    query_exist = query_exists(query)

    if query_exist:
        for row in query.limit(5).all():
            result.append({
                "code": row.Code.code,
                lengths + '_descriptor': getattr(row, length_dict.get(lengths)).descriptor
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
                'code': row.Code.code,
                'long_descriptor': row.LongDescriptor.descriptor,
                'medium_descriptor': row.MediumDescriptor.descriptor,
                'short_descriptor': row.ShortDescriptor.descriptor
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
