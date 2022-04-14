""" Clinician Descriptor endpoints """
from   abc import abstractmethod
from   dataclasses import dataclass
import logging

from   sqlalchemy import and_

from   datalabs.access.api.task import APIEndpointTask, ResourceNotFound, InvalidRequest
from   datalabs.access.cpt.api.filter import KeywordFilterMixin, WildcardFilterMixin
from   datalabs.model.cpt.api import ClinicianDescriptor, ClinicianDescriptorCodeMapping
from   datalabs.model.cpt.api import Code, Release, ReleaseCodeMapping
from   datalabs.access.cpt.api import languages
from   datalabs.access.orm import Database
from   datalabs.parameter import add_schema

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@add_schema
@dataclass
class ClinicianDescriptorsEndpointParameters:
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


class BaseClinicianDescriptorsEndpointTask(APIEndpointTask):
    PARAMETER_CLASS = ClinicianDescriptorsEndpointParameters

    def run(self):
        LOGGER.debug('Parameters: %s', self._parameters)

        with Database.from_parameters(self._parameters) as database:
            self._run(database)

    def _run(self, database):
        self._set_parameter_defaults()
        LOGGER.debug('Parameters: %s', self._parameters)

        language = self._parameters.query.get('language').lower()

        if not self._language_is_valid(language):
            raise InvalidRequest(f"Invalid query parameter: language={language}")

        query = self._query_for_descriptors(database)

        query = self._filter(query)

        self._response_body = self._generate_response_body(query.all(), language)

    def _set_parameter_defaults(self):
        self._parameters.query['keyword'] = self._parameters.query.get('keyword') or []
        self._parameters.query['language'] = self._parameters.query.get('language') or 'english'

    @classmethod
    def _query_for_descriptors(cls, database):
        return database.query(ClinicianDescriptor, ClinicianDescriptorCodeMapping).join(ClinicianDescriptorCodeMapping)

    @classmethod
    def _language_is_valid(cls, language):
        return language in languages.Descriptor_Languages

    @abstractmethod
    def _filter(self, query):
        pass

    @classmethod
    def _generate_response_body(cls, rows, language):
        return [
            dict(id=row.ClinicianDescriptor.id,
            code=row.ClinicianDescriptorCodeMapping.code,
            descriptor=getattr(row.ClinicianDescriptor, "descriptor" + languages.Descriptor_Suffix[language]),
            language=language) for row in rows
        ]


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

        # pylint: disable=singleton-comparison
        return query.filter(ClinicianDescriptor.deleted == False)

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
