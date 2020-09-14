""" Consumer Descriptor endpoint classes. """
from abc import abstractmethod
import logging

from sqlalchemy import or_, and_

from datalabs.access.api.task import APIEndpointTask, ResourceNotFound
from datalabs.model.cpt.api import ConsumerDescriptor, Release

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class BaseConsumerDescriptorEndpointTask(APIEndpointTask):
    def _run(self, session):
        LOGGER.debug('Parameters: %s', self._parameters)
        self._set_parameter_defaults()
        LOGGER.debug('Parameters: %s', self._parameters)

        query = self._query_for_descriptors(session)

        query = self._filter(query)

        self._response_body = self._generate_response_body(query.all())

    def _set_parameter_defaults(self):
        self._parameters.query['keyword'] = self._parameters.query.get('keyword') or []

    @classmethod
    def _query_for_descriptors(cls, session):
        return session.query(ConsumerDescriptor)

    @abstractmethod
    def _filter(self, query):
        pass

    @classmethod
    def _generate_response_body(cls, rows):
        return [dict(code=row.code, descriptor=row.descriptor) for row in rows]


class ConsumerDescriptorEndpointTask(BaseConsumerDescriptorEndpointTask):
    def _run(self, session):
        super()._run(session)

        if not self._response_body:
            raise ResourceNotFound('No Consumer Descriptor found for the given CPT code')

        self._response_body = self._response_body[0]

    def _filter(self, query):
        code = self._parameters.path.get('code')

        return self._filter_by_code(query, code)

    @classmethod
    def _filter_by_code(cls, query, code):
        return query.filter(ConsumerDescriptor.code == code)


class AllConsumerDescriptorsEndpointTask(BaseConsumerDescriptorEndpointTask):
    def _filter(self, query):
        since = self._parameters.query.get('since')
        keywords = self._parameters.query.get('keyword')
        code = self._parameters.query.get('code')

        query = self._filter_for_release(query, since)

        query = self._filter_for_keywords(query, keywords)

        query = self._filter_for_wildcard(query, code)

        return query

    @classmethod
    def _filter_for_release(cls, query, since):
        if since is not None:
            query = query.add_column(Release.effective_date)

            for date in since:
                query = query.filter(Release.effective_date >= date)

        return query

    @classmethod
    def _filter_for_keywords(cls, query, keywords):
        filter_conditions = [(ConsumerDescriptor.descriptor.ilike('%{}%'.format(word))) for word in keywords]

        return query.filter(or_(*filter_conditions))

    @classmethod
    def _filter_for_wildcard(cls, query, code):
        if code is not None:
            code = code.split('*')
            prefix = code[0]
            suffix = code[1]
            filter_condition = [ConsumerDescriptor.code.like(f'{prefix}%')]

            if suffix.isalpha() or suffix.isnumeric():
                filter_condition.append(ConsumerDescriptor.code.ilike(f'%{suffix}'))
            query = query.filter(and_(*filter_condition))

        return query
