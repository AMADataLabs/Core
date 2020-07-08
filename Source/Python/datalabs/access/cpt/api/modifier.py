from   abc import abstractmethod
from   collections import defaultdict
import json
import logging
import os

from   sqlalchemy import or_
from   sqlalchemy.orm.exc import NoResultFound

from   datalabs.access.task import APIEndpointTask, APIEndpointException, InvalidRequest, ResourceNotFound
from   datalabs.etl.cpt.dbmodel import Modifier, ModifierType
from   datalabs.access.database import Database

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class BaseModifierEndpointTask(APIEndpointTask):
    def _run(self, session):
        LOGGER.debug('Parameters: %s', self._parameters)
        self._set_parameter_defaults()
        LOGGER.debug('Parameters: %s', self._parameters)

        query = self._query_for_modifiers(session)

        query = self._filter(query)

        self._response_body = self._generate_response_body(query.all())

    def _set_parameter_defaults(self):
        pass

    @classmethod
    def _query_for_modifiers(cls, session):
        return session.query(Modifier, ModifierType).join(ModifierType)

    @abstractmethod
    def _filter(self, query):
        pass

    @classmethod
    def _generate_response_body(cls, rows):
        return [
            dict(
                code=row.Modifier.modifier,
                descriptor=row.Modifier.descriptor,
                type=row.ModifierType.name)
            for row in rows
        ]


class ModifierEndpointTask(BaseModifierEndpointTask):
    def _run(self, session):
        super()._run(session)

        if not self._response_body:
            raise ResourceNotFound('No data exists for the given modifier')

        self._response_body = self._response_body[0]

    def _filter(self, query):
        code = self._parameters.path.get('code')

        return self._filter_by_code(query, code)

    @classmethod
    def _filter_by_code(cls, query, code):
        return query.filter(Modifier.modifier == code)


class AllModifiersEndpointTask(BaseModifierEndpointTask):
    def _set_parameter_defaults(self):
        self._parameters.query['type'] = self._parameters.query.get('type') or []

    def _filter(self, query):
        since = self._parameters.query.get('since')
        types = self._parameters.query.get('type')

        query = self._filter_for_release(query, since)

        query = self._filter_for_type(query, types)

        return query

    def _filter_for_release(self, query, since):
        if since is not None:
            query = query.add_column(Release.effective_date)

            for date in query_parameter['since']:
                query = query.filter(Release.effective_date >= date)

        return query

    def _filter_for_type(self, query, types):
        filter_conditions = [(ModifierType.name == t) for t in types]

        return query.filter(or_(*filter_conditions))
