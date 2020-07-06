import json
import os

from   sqlalchemy import create_engine
from   sqlalchemy.orm import sessionmaker

import datalabs.access.credentials as credentials
import datalabs.access.database as database
from   datalabs.access.task import APIEndpointTask
from   datalabs.etl.cpt.dbmodel import Code, ShortDescriptor, LongDescriptor, MediumDescriptor
from   datalabs.access.database import Database


def lambda_handler(event, context):
    DescriptorEndpointTask(event).run()


class DescriptorEndpointTask(APIEndpointTask):
    def run(self):
        with self._get_database() as database:
            path_parameter = self._event.get('pathParameters', None)

            query = self.query_for_descriptor(database.session, path_parameter)
            status_code, response = self._get_response_data_from_query(query, path_parameter.get('lengths', None))

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
    def query_for_descriptor(cls, session, path_parameter):
        query = None

        if path_parameter is not None:
            query = session.query(Code, LongDescriptor, MediumDescriptor, ShortDescriptor).join(LongDescriptor,
                                                                                                MediumDescriptor,
                                                                                                ShortDescriptor)
            query = query.filter(Code.code == path_parameter['code'])

        return query

    @classmethod
    def _get_response_data_from_query(cls, query, lengths):
        if lengths is not None:
            if cls._lengths_exist(lengths):
                status_code, response_data = cls._get_filtered_length_response(query, lengths)
            else:
                status_code = 400
                response_data = 'Invalid query parameter'
        else:
            status_code, response_data = cls._get_content_from_query(query)

        return status_code, response_data

    @classmethod
    def _lengths_exist(cls, lengths):
        length_dict = {"long": LongDescriptor, "medium": MediumDescriptor, "short": ShortDescriptor}
        return all([length in lengths for length in length_dict.keys()])

    @classmethod
    def _get_filtered_length_response(cls, query, lengths):
        response_data = []
        length_dict = {"long": 'LongDescriptor', "medium": 'MediumDescriptor', "short": 'ShortDescriptor'}

        if query is not None:
            for row in query.all():
                response_row = {"code": row.Code.code}

                for length in lengths:
                    response_row.update({length + '_descriptor': getattr(row, length_dict.get(length)).descriptor})

                response_data.append(response_row)
            status_code = 200

        else:
            response_data = 'No descriptor found for the given CPT Code'
            status_code = 404

        return status_code, response_data

    @classmethod
    def _get_content_from_query(cls, query):
        if query is not None:
            response_row = [dict(
                code=row.Code.code,
                long_descriptor=row.LongDescriptor.descriptor,
                medium_descriptor=row.MediumDescriptor.descriptor,
                short_descriptor=row.ShortDescriptor.descriptor, ) for row in query.all()]
            status_code = 200
        else:
            response_row = 'No descriptor found for the given CPT Code'
            status_code = 404

        return status_code, response_row
