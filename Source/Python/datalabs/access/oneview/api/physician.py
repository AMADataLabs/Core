""" OneView Physician endpoint classes """
import logging

from   sqlalchemy import func, or_
from   sqlalchemy.orm import defer, undefer

from   datalabs.access.api.task import APIEndpointTask, ResourceNotFound, InvalidRequest
from   datalabs.model.masterfile.oneview.content import Physician

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class PhysiciansEndpointTask(APIEndpointTask):
    def _run(self, database):
        LOGGER.debug('Parameters: %s', self._parameters)
        LOGGER.debug('Parameters: %s', self._parameters)

        query = self._query_for_physicians(database)

        query, fields, query_params, filter_conditions = self._filter(query)

        self._response_body = self._generate_response_body(query.all(), fields, query_params,filter_conditions)

        if not self._response_body:
            raise ResourceNotFound('No data exists for the given column filters')

        self._response_body = self._response_body[0]

    @classmethod
    def _query_for_physicians(cls, database):
        return database.query(Physician)

    def _filter(self, query):
        query_params = self._parameters.query
        return_fields = query_params.pop("field", None)

        query, filter_conditions = self._filter_by_fields(query, query_params)
        if return_fields is not None:
            query = self._filter_return_fields(query, return_fields)

        # pylint: disable=singleton-comparison
        return query, return_fields, query_params, filter_conditions

    @classmethod
    def _generate_response_body(cls, rows, return_fields, query_params, filter_conditions):
        # pylint: disable=no-member
        columns = return_fields or [column.name for column in Physician.__table__.columns.keys()]
        output = []

        # If return fields is not specified
        for row in rows:
            for column in columns:
                row_data = {column: getattr(row, column)}
                output.append(row_data)

        output.append({'query_params': query_params})
        output.append({'rows': columns})
        output.append({'filter': filter_conditions})

        return output

    @classmethod
    def _filter_by_fields(cls, query, query_params):
        # Add WHERE filters to query
        filter_conditions = []

        for fields, values in query_params.items():
            if hasattr(Physician, fields) is False:
                raise InvalidRequest(f"Invalid table field: {field}")

            filter_conditions = cls._query_for_values(values, fields, filter_conditions)

        query = query.filter(or_(*filter_conditions))

        return query, filter_conditions

    @classmethod
    def _filter_return_fields(cls, query, return_fields):
        # Remove all columns from SELECT statement
        query = query.options(defer('*'))

        # Add back in specified fields to SELECT
        for field in return_fields:
            query = query.options(undefer(getattr(Physician, field)))

        return query

    @classmethod
    def _query_for_values(cls, values, field, filter_conditions):
        for value in values:
            if value.isnumeric() is False:
                func.lower(value)
            filter_conditions += [(func.lower(getattr(Physician, field)) == value)]

        return filter_conditions
