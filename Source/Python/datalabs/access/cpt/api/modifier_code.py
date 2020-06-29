import sqlalchemy
import json
from   sqlalchemy import create_engine, or_
from   sqlalchemy.orm import sessionmaker
from   datalabs.etl.cpt.dbmodel import Modifier, ModifierType
from   datalabs.access.database import Database


def lambda_handler(event, context):
    session = create_database_connection()
    query = query_for_modifier(session, event.get('pathParameters', None))

    status_code, response = get_content_from_query(query)

    return {'statusCode': status_code, 'body': json.dumps(response)}


def create_database_connection():
    engine = create_engine(Database.url)
    Session = sessionmaker(bind=engine)
    return Session()


def query_for_modifier(session, path_parameter):
    query = None

    if path_parameter is not None:
        query = session.query(Modifier, ModifierType).join(ModifierType)
        query = query.filter(Modifier.modifier == path_parameter['code'])

    return query


def get_content_from_query(query):

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
        response_rows = {"invalid": "type"}

    return status_code, response_rows
