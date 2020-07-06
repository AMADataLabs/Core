from   collections import defaultdict
import json
import os

from   sqlalchemy import create_engine
from   sqlalchemy.orm import sessionmaker

import datalabs.access.credentials as credentials
import datalabs.access.database as database
from   datalabs.access.task import APIEndpointTask, APIException, InvalidRequest, ResourceNotFound
from   datalabs.etl.cpt.dbmodel import Code, ShortDescriptor, LongDescriptor, MediumDescriptor
from   datalabs.access.database import Database


def lambda_handler(event, context):
    status_code = 200
    response = None

    try:
        response = DescriptorEndpointTask(event).run()
    except APIException as exception:
        status_code = exception.status_code
        response = dict(message=str(exception))

    return {
        "statusCode": status_code,
        "body": json.dumps(response)
    }


class DescriptorEndpointTask(APIEndpointTask):
    LENGTH_MODEL_NAMES = dict(short='ShortDescriptor', medium='MediumDescriptor', long='LongDescriptor')

    def run(self):
        with self._get_database() as database:
            path_parameters = self._event.get('pathParameters', dict())
            code = path_parameters.get('code')
            multi_value_parameters = self._event.get('multiValueQueryStringParameters', defaultdict(list))
            lengths = multi_value_parameters.get('length') or ['short', 'medium', 'long']

            if not cls._lengths_are_valid(lengths):
                raise InvalidRequest("Invalid query parameter")

            query = self._query_for_descriptor(database.session, code)

            if query is None:
                raise ResourceNotFound('No descriptor found for the given CPT Code')

            return cls._generate_response_body(query.one(), lengths)

    @classmethod
    def _get_database(cls):
        database_key = os.environ['LAMBDA_FUNCTION_CPTGETDESCRIPTOR_DATABASE']
        database_config = database.Configuration.load(database_key)
        database_credentials = credentials.Credentials.load(database_key)

        return database.Database(database_config, database_credentials)

    @classmethod
    def _lengths_are_valid(cls, lengths):
        return all(length in cls.LENGTH_MODEL_NAMES.keys() for length in lengths)

    @classmethod
    def _query_for_descriptor(cls, session, code):
        query = None

        if code is not None:
            query = session.query(Code, LongDescriptor, MediumDescriptor, ShortDescriptor).join(
                LongDescriptor, MediumDescriptor, ShortDescriptor
            )
            query = query.filter(Code.code == code)

        return query

    @classmethod
    def _generate_response_body(cls, row, lengths):
        body = dict(code=row.Code.code)

        for length in lengths:
            body.update({length + '_descriptor': getattr(row, cls.LENGTH_MODEL_NAMES[length]).descriptor})

        return body
