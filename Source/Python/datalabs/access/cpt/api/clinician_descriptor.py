""" Clinician Descriptor endpoints """
from   abc import abstractmethod
import logging

from   sqlalchemy import and_

from   datalabs.access.api.task import APIEndpointTask, ResourceNotFound
from   datalabs.access.cpt.api.filter import KeywordFilterMixin, WildcardFilterMixin
from   datalabs.model.cpt.api import ClinicianDescriptor, ClinicianDescriptorCodeMapping
from   datalabs.model.cpt.api import Code, Release, ReleaseCodeMapping

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class BaseClinicianDescriptorsEndpointTask(APIEndpointTask):
    def _run(self, database):
        LOGGER.debug('Parameters: %s', self._parameters)
        self._set_parameter_defaults()
        LOGGER.debug('Parameters: %s', self._parameters)

        query = self._query_for_descriptors(database)

        query = self._filter(query)

        self._response_body = self._generate_response_body(query.all())

    def _set_parameter_defaults(self):
        self._parameters.query['keyword'] = self._parameters.query.get('keyword') or []

    @classmethod
    def _query_for_descriptors(cls, database):
        return database.query(ClinicianDescriptor, ClinicianDescriptorCodeMapping).join(ClinicianDescriptorCodeMapping)

    @abstractmethod
    def _filter(self, query):
        pass

    @classmethod
    def _generate_response_body(cls, rows):
        return [dict(id=row.ClinicianDescriptor.id,
                     code=row.ClinicianDescriptorCodeMapping.code,
                     descriptor=row.ClinicianDescriptor.descriptor) for row in rows]


class ClinicianDescriptorsEndpointTask(BaseClinicianDescriptorsEndpointTask):
    def _run(self, database):
        super()._run(database)

        if not self._response_body:
            raise ResourceNotFound('No Clinician Descriptors found for the given CPT code')

        self._response_body = self._response_body

    def _filter(self, query):
        code = self._parameters.path.get('code')
        query = self._filter_by_code(query, code)

        # pylint: disable=singleton-comparison
        return query.filter(ClinicianDescriptor.deleted == False)

    @classmethod
    def _filter_by_code(cls, query, code):
        return query.filter(ClinicianDescriptorCodeMapping.code == code)


# pylint: disable=too-many-ancestors
class AllClinicianDescriptorsEndpointTask(
        BaseClinicianDescriptorsEndpointTask,
        KeywordFilterMixin,
        WildcardFilterMixin
):
    # pylint: disable=no-self-use
    def _filter(self, query):
        since = self._parameters.query.get('since')
        keywords = self._parameters.query.get('keyword')
        code = self._parameters.query.get('code')

        query = self._filter_for_release(query, since)

        query = self._filter_for_keywords([ClinicianDescriptor.descriptor], query, keywords)

        query = self._filter_for_wildcard(ClinicianDescriptorCodeMapping, query, code)

        return query

    @classmethod
    def _filter_for_release(cls, query, since):
        if since is not None:
            for date in since:
                query = query.filter(and_(
                    ClinicianDescriptorCodeMapping.code == Code.code,
                    ClinicianDescriptorCodeMapping.clinician_descriptor == ClinicianDescriptor.id,
                    ReleaseCodeMapping.code == Code.code,
                    ReleaseCodeMapping.release == Release.id,
                    Release.effective_date >= date
                ))

        return query
