""" CPT Modifier endpoint classes. """
from   abc import abstractmethod
import logging

from   sqlalchemy import or_

from   datalabs.access.api.task import APIEndpointTask, ResourceNotFound
from   datalabs.model.cpt.api import Modifier, ModifierType, Release

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class BaseModifierEndpointTask(APIEndpointTask):
    def _run(self, database):
        LOGGER.debug('Parameters: %s', self._parameters)
        self._set_parameter_defaults()
        LOGGER.debug('Parameters: %s', self._parameters)

        query = self._query_for_modifiers(database)

        query = self._filter(query)

        self._response_body = self._generate_response_body(query.all())

    def _set_parameter_defaults(self):
        pass

    @classmethod
    def _query_for_modifiers(cls, database):
        return database.query(Modifier, ModifierType).join(ModifierType)

    @abstractmethod
    def _filter(self, query):
        pass

    @classmethod
    def _generate_response_body(cls, rows):
        return [
            dict(
                code=row.Modifier.modifier,
                descriptor=row.Modifier.descriptor,
                type=row.ModifierType.name,
                general_use=row.Modifier.general,
                ambulatory_service_center=row.Modifier.ambulatory_service_center
            )
            for row in rows
        ]


class ModifierEndpointTask(BaseModifierEndpointTask):
    def _run(self, database):
        super()._run(database)

        if not self._response_body:
            raise ResourceNotFound('No data exists for the given modifier')

        self._response_body = self._response_body[0]

    def _filter(self, query):
        code = self._parameters.path.get('code')
        query = self._filter_by_code(query, code)

        # pylint: disable=singleton-comparison
        return query.filter(Modifier.deleted == False)

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

    @classmethod
    def _filter_for_release(cls, query, since):
        if since is not None:
            query = query.add_column(Release.effective_date)

            for date in since:
                query = query.filter(Release.effective_date >= date)

        else:
            query = query.filter(Modifier.deleted == False)  # pylint: disable=singleton-comparison

        return query

    @classmethod
    def _filter_for_type(cls, query, types):
        filter_conditions = [(ModifierType.name == t) for t in types]

        return query.filter(or_(*filter_conditions))
