""" OneView Physician endpoint classes """
from   abc import abstractmethod
import logging

from   sqlalchemy import or_, func
from sqlalchemy.orm import defer, undefer

from   datalabs.access.api.task import APIEndpointTask, ResourceNotFound
from   datalabs.model.masterfile.oneview import Physician

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class BasePhysicianEndpointTask(APIEndpointTask):
    def _run(self, database):
        LOGGER.debug('Parameters: %s', self._parameters)
        self._set_parameter_defaults()
        LOGGER.debug('Parameters: %s', self._parameters)

        query = self._query_for_physicians(database)

        query, fields = self._filter(query)

        self._response_body = self._generate_response_body(query.all(), fields)

    def _set_parameter_defaults(self):
        pass

    @classmethod
    def _query_for_physicians(cls, database):
        return database.query(Physician)

    @abstractmethod
    def _filter(self, query):
        pass

    @classmethod
    def _generate_response_body(cls, rows, fields):

        output = []

        # If return fields is not specified
        if len(fields) == 0:
            for row in rows:
                d = vars(row)

                # vars(row) has the SQLAlchemy State Instance as a key, so this removes it manually
                # If there is some way to take the Query and return a dict more eloquently, that would be nice
                d.pop("_sa_instance_state")
                output.append(d)
        else:
            for row in rows:
                d = {}
                for column in fields:
                    d[column] = str(getattr(row, column))
                output.append(d)

        print("\n")
        print(" === GET REQUEST OUTPUT === ")
        for r in output:
            print(r)
        print("\n")


        return output

class PysicianEndpointTask(BasePhysicianEndpointTask):
    def _run(self, database):
        super()._run(database)

        if not self._response_body:
            raise ResourceNotFound('No data exists for the given modifier')

        self._response_body = self._response_body[0]

    def _filter(self, query):
        fields = self._parameters.query

        query, return_fields = self._filter_by_fields(query, fields)

        # pylint: disable=singleton-comparison
        return query, return_fields

    @classmethod
    def _filter_by_fields(cls, query, fields):

        return_fields = []

        if "field" in fields:
            # Remove all columns from SELECT statment
            query = query.options(defer('*'))

            return_fields = fields.pop("field")

            # Add back in specified fields to SELECT
            for f in return_fields:
                query = query.options(undefer(getattr(Physician, f)))

        # Add WHERE filters to query
        for attr, value in fields.items():
            query = query.filter(func.lower(getattr(Physician, attr)) == func.lower(value))

        return query, return_fields