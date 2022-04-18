""" OneView Physician endpoint classes """
from   dataclasses import dataclass
import logging

from   sqlalchemy import func, or_

from   datalabs.access.api.task import APIEndpointTask, ResourceNotFound, InvalidRequest
from   datalabs.model.masterfile.oneview.content import Physician
from   datalabs.access.orm import Database
from   datalabs.parameter import add_schema

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=too-many-instance-attributes
@add_schema(unknowns=True)
@dataclass
class PhysiciansEndpointParameters:
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


class PhysiciansEndpointTask(APIEndpointTask):
    PARAMETER_CLASS = PhysiciansEndpointParameters

    def run(self):
        LOGGER.debug('Parameters: %s', self._parameters)

        with Database.from_parameters(self._parameters) as database:
            self._run(database)

    def _run(self, database):
        LOGGER.debug('Parameters: %s', self._parameters)
        LOGGER.debug('Parameters: %s', self._parameters)

        query = self._query_for_physicians(database)

        query, fields = self._filter(query)

        self._response_body = self._generate_response_body(query.all(), fields)

        if not self._response_body:
            raise ResourceNotFound('No data exists for the given column filters')

        self._response_body = self._response_body

    @classmethod
    def _query_for_physicians(cls, database):
        return database.query(Physician)

    def _filter(self, query):
        query_params = self._parameters.query
        return_fields = query_params.pop("field", None)

        query = self._filter_by_fields(query, query_params)

        # pylint: disable=singleton-comparison
        return query, return_fields

    @classmethod
    def _generate_response_body(cls, rows, return_fields):
        # pylint: disable=no-member
        if return_fields is None:
            return_fields = [column.key for column in Physician.__table__.columns]
        output = []

        # If return fields is not specified
        for row in rows:
            row_data = {column: getattr(row, column) for column in return_fields}
            output.append(row_data)

        return output

    @classmethod
    def _filter_by_fields(cls, query, query_params):
        # Add WHERE filters to query
        filter_conditions = []

        for field, values in query_params.items():
            if hasattr(Physician, field) is False:
                raise InvalidRequest(f"Invalid table field: {field}")

            filter_conditions = cls._query_for_values(values, field, filter_conditions)

        query = query.filter(or_(*filter_conditions))

        return query

    @classmethod
    def _query_for_values(cls, values, field, filter_conditions):
        for value in values:
            filter_conditions += [(func.lower(getattr(Physician, field)) == value)]

        return filter_conditions
