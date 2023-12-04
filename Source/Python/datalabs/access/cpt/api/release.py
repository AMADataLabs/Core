""" Release endpoint classes. """
from   dataclasses import dataclass
import logging
import psycopg2
import re
from psycopg2 import OperationalError, errors

from   datalabs.access.api.task import APIEndpointTask, InvalidRequest
from   datalabs.model.cpt.api import Release
from   datalabs.access.orm import Database
from   datalabs.parameter import add_schema

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=too-many-instance-attributes
@add_schema(unknowns=True)
@dataclass
class ReleasesEndpointParameters:
    method: str
    path: dict
    query: dict
    authorization: dict
    database_name: str
    database_backend: str
    database_host: str
    database_port: str
    database_username: str
    database_password: str
    unknowns: dict=None


class ReleasesEndpointTask(APIEndpointTask):
    PARAMETER_CLASS = ReleasesEndpointParameters

    def run(self):
        LOGGER.debug('Parameters: %s', self._parameters)

        with Database.from_parameters(self._parameters) as database:
            self._run(database)

    def _run(self, database):
        self._set_parameter_defaults()

        max_results = self._parameters.query.get('results')
        if not self._max_results_is_valid(max_results):
            raise InvalidRequest(f'Invalid query parameter: results={max_results}')

        query = self._query_for_releases(database)

        query = self._filter_for_max_results(query)

        try:
            self._response_body = self._generate_response_body(query.all())
        except psycopg2.OperationalError as e:
            masked_error_message = self._mask_host_details(str(e))
            self._response_body = f"OperationalError: {masked_error_message}"

    def _set_parameter_defaults(self):
        self._parameters.query['results'] = self._parameters.query.get('results')
        if self._parameters.query['results'] is not None and not hasattr(self._parameters.query['results'], 'isdigit'):
            self._parameters.query['results'] = self._parameters.query.get('results')[0]

        self._parameters.query['keyword'] = self._parameters.query.get('keyword') or []

    @classmethod
    def _max_results_is_valid(cls, max_results):
        valid = False

        if max_results and max_results.isdigit() and int(max_results) > 0:
            valid = True
        elif max_results is None:
            valid = True

        return valid

    @classmethod
    def _query_for_releases(cls, database):
        return database.query(Release).order_by(Release.date.desc())

    def _filter_for_max_results(self, query):
        max_results = self._parameters.query.get('results')

        if max_results is not None:
            query = query.limit(max_results)

        return query

    @classmethod
    def _generate_response_body(cls, rows):
        return [
            dict(
                id=row.id,
                date=str(row.date),
            )
            for row in rows
        ]

    @classmethod
    def _mask_host_details(self, error_message):
        masked_message = re.sub(r'at "[^"]+" \(.*\), port \d+', 'at {masked_host}', error_message)
        return masked_message