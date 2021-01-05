""" Consumer Descriptor endpoint classes. """
from   abc import abstractmethod
import logging

from   datalabs.access.api.task import APIEndpointTask, ResourceNotFound
from   datalabs.access.cpt.api.filter import KeywordFilterMixin, WildcardFilterMixin
from   datalabs.model.cpt.api import ConsumerDescriptor, Release

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class BaseConsumerDescriptorEndpointTask(APIEndpointTask):
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
        return database.query(ConsumerDescriptor)

    @abstractmethod
    def _filter(self, query):
        pass

    @classmethod
    def _generate_response_body(cls, rows):
        return [dict(code=row.code, descriptor=row.descriptor) for row in rows]


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
class AllConsumerDescriptorsEndpointTask(BaseConsumerDescriptorEndpointTask, KeywordFilterMixin, WildcardFilterMixin):
    def _filter(self, query):
        since = self._parameters.query.get('since')
        keywords = self._parameters.query.get('keyword')
        code = self._parameters.query.get('code')

        query = self._filter_for_release(query, since)

        query = self._filter_for_keywords([ConsumerDescriptor.descriptor], query, keywords)

        query = self._filter_for_wildcard(ConsumerDescriptor, query, code)

        return query

    @classmethod
    def _filter_for_release(cls, query, since):
        if since is not None:
            query = query.add_column(Release.effective_date)

            for date in since:
                query = query.filter(Release.effective_date >= date)

        else:
            query = query.filter(ConsumerDescriptor.deleted == False)  # pylint: disable=singleton-comparison

        return query
