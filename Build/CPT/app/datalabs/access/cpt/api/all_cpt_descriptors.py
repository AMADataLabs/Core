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
    if 'keyword' not in list(event.keys()) and 'since' not in list(event.keys()):
        return query_all(event, session)
    else:
        since = event.get('since', None)
        keyword = event.get('keyword', None)
        return query_filters(session, since, keyword, event)


def query_all(event, session):
    query = session.query(Code, LongDescriptor, ShortDescriptor, MediumDescriptor)
    return filter_length(query, event)


def query_filters(session, since, keyword, event):
    if since == None:
        query = session.query(Code, LongDescriptor, ShortDescriptor, MediumDescriptor).join(LongDescriptor,
                                                                                            ShortDescriptor,
                                                                                            MediumDescriptor) \
            .filter(or_((LongDescriptor.descriptor.like('%{}%'.format(keyword))),
                        (MediumDescriptor.descriptor.like('%{}%'.format(keyword))),
                        (ShortDescriptor.descriptor.like('%{}%'.format(keyword)))))
        print(query)
    elif keyword == None:
        d_type = date_type(since)
        query = session.query(Release).join(Code, LongDescriptor, MediumDescriptor, ShortDescriptor) \
            .filter(getattr(Release, d_type).like('%{}%'.format(since)))
    else:
        d_type = date_type(since)
        query = session.query(LongDescriptor, ShortDescriptor, MediumDescriptor, Release).join(Code) \
            .filter(getattr(Release, d_type).like('%{}%'.format(since))).filter(
            or_(LongDescriptor.descriptor.like('%{}%'.format(keyword))),
            (MediumDescriptor.descriptor.like('%{}%'.format(keyword))),
            (ShortDescriptor.descriptor.like('%{}%'.format(keyword))))

    print(query)
    if query.count() == 0:
        return 400, {'filter': 'not found'}
    else:
        return filter_length(query, event)


def date_type(since):
    # check format
    # return annual,date,or quarterly
    date_type_table = 'publish_date'
    return date_type_table


def filter_length(query, event):
    length = event.get('length', None)
    if length != None:
        return get_filtered_content_from_query(query, event)
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


def get_filtered_content_from_query(query, event):
    lengths = event.get('length', None)
    length_dict = {"long": 'LongDescriptor', "medium": 'MediumDescriptor', "short": 'ShortDescriptor'}
    record = {}
    for row in query:
        record.update({'code': row.Code.code})
        for length in lengths:
            length = length_dict.get(length)
            record.update({length: getattr(row, length).descriptor})

    return 200, record
