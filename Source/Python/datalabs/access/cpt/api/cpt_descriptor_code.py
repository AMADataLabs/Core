import json
import os

from   sqlalchemy import create_engine
from   sqlalchemy.orm import sessionmaker

import datalabs.access.credentials as credentials
import datalabs.access.database as database
from   datalabs.access.task import APIEndpointTask
from   datalabs.etl.cpt.dbmodel import Code, ShortDescriptor, LongDescriptor, MediumDescriptor


def lambda_handler(event, context):
    DescriptorEndpointTask(event).run()


class DescriptorEndpointTask(APIEndpointTask):
    def run(self):
        with self._get_database() as database:
            query = query_for_descriptor(database.session)
            query = _query_by_code(query, self._event)
            status_code = 200

            if self._event.get('multiValueQueryStringParameters', None) is not None:
                status_code, response = _get_filtered_length_response(query, self._event['multiValueQueryStringParameters']['length'])
            else:
                response = _get_content_from_query(query)

            return {
                "statusCode": status_code,
                "body": json.dumps(response)
            }

    @classmethod
    def _get_database(cls):
        database_key = os.environ['LAMBDA_FUNCTION_CPTGETDESCRIPTOR_DATABASE']
        database_config = database.Configuration.load(database_key)
        database_credentials = credentials.Credentials.load(database_key)

        return database.Database(database_config, database_credentials)

    @classmethod
    def query_for_descriptor(cls, session):
        query = session.query(Code, LongDescriptor, MediumDescriptor, ShortDescriptor).join(LongDescriptor,
                                                                                            MediumDescriptor,
                                                                                            ShortDescriptor)
        return query

    @classmethod
    def _query_by_code(cls, query, event):
        if event.get('pathParameters', None) is not None:
            query = query.filter(Code.code == event['pathParameters']['code'])

        else:
            query = None

        return query


    @classmethod
    def _get_response_data_from_query(cls, query, event):
        lengths = event["multiValueQueryStringParameters"].get('length', None)

        if lengths is not None:
            if _lengths_exist(lengths):
                response_data = _get_filtered_length_response(query, lengths)
                status_code = 200
            else:
                status_code = 400
                response_data = {'length(s)': 'invalid'}
        else:
            response_data = _get_content_from_query(query)
            status_code = 200

        return status_code, response_data


    @classmethod
    def _lengths_exist(cls, lengths):
        length_dict = {"long": LongDescriptor, "medium": MediumDescriptor, "short": ShortDescriptor}

        for length in lengths:
            if length in list(length_dict.keys()):
                condition = True
            else:
                condition = False
                break

        return condition


    @classmethod
    def _get_filtered_length_response(cls, query, lengths):
        response_data = []
        length_dict = {"long": 'LongDescriptor', "medium": 'MediumDescriptor', "short": 'ShortDescriptor'}
        if not lengths:
            lengths = ['short', 'medium', 'long']

        if query is not None:
            for row in query.all():
                response_row = {"code": row.Code.code}
                for length in lengths:
                    response_row.update({length + '_descriptor': getattr(row, length_dict.get(length)).descriptor})

                response_data.append(response_row)
        else:
            response_data = {'code': 'not given'}

        return response_data


    @classmethod
    def _get_content_from_query(cls, query):
        response_row = []
        print(query)
        if query is not None:
            for row in query.all():
                response_data = {
                    'code': row.Code.code,
                    'long_descriptor': row.LongDescriptor.descriptor,
                    'medium_descriptor': row.MediumDescriptor.descriptor,
                    'short_descriptor': row.ShortDescriptor.descriptor
                }
                response_row.append(response_data)
        else:
            response_row = {'code': 'not given'}

        return response_row


