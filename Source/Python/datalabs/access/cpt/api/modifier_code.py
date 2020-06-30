import sqlalchemy
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker
from datalabs.etl.cpt.dbmodel import Modifier, ModifierType
from datalabs.access.database import Database


def lambda_handler(event, context):
    engine = create_engine(Database.url)
    Session = sessionmaker(bind=engine)
    session = Session()

    status_code, response = query_event(event, session)
    return {'statusCode': status_code, 'body': response}


def query_event(event, session):
    query = query_for_descriptor(session)
    return query_for_code(event.get('code', None), query)


def query_for_descriptor(session):
    query = session.query(Modifier, ModifierType).join(ModifierType)
    return query


def query_for_code(code, query):
    if code is not None:
        query = query.filter((Modifier.modifier.like(code)))
        return get_response_data_from_query(query)
    else:
        return 400, {"Error": "No code given"}


def get_response_data_from_query(query):
    result = []
    query_exist = query_exists(query)

    if query_exist:
        for row in query.all():
            record = {
                'code': row.Modifier.modifier,
                'descriptor': row.Modifier.descriptor,
                'type': row.ModifierType.name
            }
            result.append(record)

        return 200, result
    else:
        return 400, {"invalid": "type"}


def query_exists(query):
    if query.count() == 0:
        return False
    else:
        return True
