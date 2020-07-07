import sqlalchemy
import json
from   sqlalchemy import create_engine, or_
from   sqlalchemy.orm import sessionmaker
from   datalabs.etl.cpt.dbmodel import Modifier, ModifierType
from   datalabs.access.database import Database


def lambda_handler(event, context):
    query_parameter = event.get('multiValueQueryStringParameters', None)

    session = create_database_connection()
    query = query_for_modifier(session)

    if query_parameter is not None:
        query = filter_query_for_type(query_parameter.get('type', None), query_parameter, query)

    status_code, response = get_response_data_from_query(query)

    return {
        "statusCode": status_code,
        "body": json.dumps(response)
    }


def create_database_connection():
    engine = create_engine(Database.url)
    Session = sessionmaker(bind=engine)
    return Session()


def query_for_modifier(session):
    query = session.query(Modifier, ModifierType).join(ModifierType)
    return query


def filter_query_for_type(mod_type, query_parameter, query):
    if mod_type is not None:
        filter_types = [ModifierType.name.ilike(('%{}%'.format(modifier_type)))
                        for modifier_type in query_parameter['type']]
        query = query.filter(or_(*filter_types))

    return query


def get_response_data_from_query(query):
    if query.count() != 0:
        response_rows = [
            dict(
                code=row.Modifier.modifier,
                descriptor=row.Modifier.descriptor,
                type=row.ModifierType.name)
            for row in query.all()
        ]
        status_code = 200
    else:
        status_code = 400
        response_rows = 'Invalid query parameter'

    return status_code, response_rows
