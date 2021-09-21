""" Consumer Descriptor endpoint classes. """
from   abc import abstractmethod
import logging

from   datalabs.access.api.task import APIEndpointTask, ResourceNotFound, InvalidRequest
from   datalabs.access.cpt.api.filter import ReleaseFilterMixin, KeywordFilterMixin, WildcardFilterMixin
from   datalabs.model.cpt.api import ConsumerDescriptor
from   datalabs.access.cpt.api import languages

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class BaseConsumerDescriptorEndpointTask(APIEndpointTask):
    def _run(self, database):
        LOGGER.debug('Parameters: %s', self._parameters)
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
        return database.query(ConsumerDescriptor)

    @classmethod
    def _language_is_valid(cls, language):
        return language.lower() in languages.Descriptor_Languages

    @abstractmethod
    def _filter(self, query):
        pass

    @classmethod
    def _generate_response_body(cls, rows, language):
        return [
            dict(code=row.code,
            descriptor=getattr(row, "descriptor" + languages.Descriptor_Suffix[language]),
            language=language) for row in rows
        ]


class ConsumerDescriptorEndpointTask(BaseConsumerDescriptorEndpointTask):
    def _run(self, database):
        super()._run(database)

        if not self._response_body:
            raise ResourceNotFound('No Consumer Descriptor found for the given CPT code')

        self._response_body = self._response_body[0]

    def _filter(self, query):
        code = self._parameters.path.get('code')
        query = self._filter_by_code(query, code)

        # pylint: disable=singleton-comparison
        return query.filter(ConsumerDescriptor.deleted == False)

    @classmethod
    def _filter_by_code(cls, query, code):
        return query.filter(ConsumerDescriptor.code == code)


# pylint: disable=too-many-ancestors
class AllConsumerDescriptorsEndpointTask(
        BaseConsumerDescriptorEndpointTask,
        ReleaseFilterMixin,
        KeywordFilterMixin,
        WildcardFilterMixin
):
    def _filter(self, query):
        since = self._parameters.query.get('since')
        keywords = self._parameters.query.get('keyword')
        code = self._parameters.query.get('code')

        query = self._filter_for_release(ConsumerDescriptor, query, since)

        query = self._filter_for_keywords([ConsumerDescriptor.descriptor], query, keywords)

        query = self._filter_for_wildcard(ConsumerDescriptor, query, code)

        return query
