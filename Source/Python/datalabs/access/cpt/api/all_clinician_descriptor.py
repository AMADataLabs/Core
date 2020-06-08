from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datalabs.etl.cpt.dbmodel import ClinicianDescriptor, ClinicianDescriptorCodeMapping, Release
from datalabs.access.database import Database


def lambda_handler(event, context):
    engine = create_engine(Database.url)
    Session = sessionmaker(bind=engine)
    session = Session()

    status_code, response = query_event(event, session)
    return {'statusCode': status_code, 'body': response}


def query_event(event, session):
    if 'keyword' not in list(event.keys()) and 'since' not in list(event.keys()):
        query = session.query(ClinicianDescriptor, ClinicianDescriptorCodeMapping)
        return get_content_from_query(query)
    else:
        since = event.get('since', None)
        keyword = event.get('keyword', None)
        return query_filters(session, since, keyword)


def get_content_from_query(query):
    all_rows = []
    for row in query:
        record = {
            'id': row.ClinicianDescriptor.id,
            'code': row.ClinicianDescriptorCodeMapping.code,
            'descriptor': row.ClinicianDescriptor.descriptor
        }
        all_rows.append(record)
    return 200, all_rows


def query_filters(session, since, keyword):
    if since == None:
        query = session.query(ClinicianDescriptor, ClinicianDescriptorCodeMapping).join(ClinicianDescriptorCodeMapping) \
            .filter(ClinicianDescriptor.descriptor.like('%{}%'.format(keyword)))
    elif keyword == None:
        d_type = date_type(since)
        query = session.query(ClinicianDescriptor, ClinicianDescriptorCodeMapping).join(ClinicianDescriptorCodeMapping,
                                                                                        Release) \
            .filter(getattr(Release, d_type).like('%{}%'.format(since)))
    else:
        d_type = date_type(since)
        query = session.query(ClinicianDescriptor, ClinicianDescriptorCodeMapping).join(ClinicianDescriptorCodeMapping,
                                                                                        Release) \
            .filter(getattr(Release, d_type).like('%{}%'.format(since))).filter(
            ClinicianDescriptor.descriptor.like('%{}%'.format(keyword)))

    if query.count() == 0:
        return 400, {'filter': 'not found'}
    else:
        return get_content_from_query(query)


def date_type(since):
    # check format
    # return annual,date,or quaterly
    date_type_table = 'publish_date'
    return date_type_table
