""" Clinician Descriptor endpoints """
from abc import abstractmethod
import logging

from sqlalchemy import or_, and_

from datalabs.access.api.task import APIEndpointTask, ResourceNotFound
from datalabs.model.cpt.api import ClinicianDescriptor, ClinicianDescriptorCodeMapping, Release

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class BaseClinicianDescriptorsEndpointTask(APIEndpointTask):
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
        return session.query(ClinicianDescriptor, ClinicianDescriptorCodeMapping).join(ClinicianDescriptorCodeMapping)

    @abstractmethod
    def _filter(self, query):
        pass

    @classmethod
    def _generate_response_body(cls, rows):
        return [dict(id=row.ClinicianDescriptor.id,
                     code=row.ClinicianDescriptorCodeMapping.code,
                     descriptor=row.ClinicianDescriptor.descriptor) for row in rows]


class ClinicianDescriptorsEndpointTask(BaseClinicianDescriptorsEndpointTask):
    def _run(self, session):
        super()._run(session)

        if not self._response_body:
            raise ResourceNotFound('No Clinician Descriptors found for the given CPT code')

        self._response_body = self._response_body

    def _filter(self, query):
        code = self._parameters.path.get('code')
        query = self._filter_by_code(query, code)

        return query.filter(ClinicianDescriptor.deleted == False)

    @classmethod
    def _filter_by_code(cls, query, code):
        return query.filter(ClinicianDescriptorCodeMapping.code == code)


class AllClinicianDescriptorsEndpointTask(BaseClinicianDescriptorsEndpointTask):
    # pylint: disable=no-self-use
    def _filter(self, query):
        since = self._parameters.query.get('since')
        keywords = self._parameters.query.get('keyword')
        code = self._parameters.query.get('code')

        query = self._filter_for_release(query, since)

        query = self._filter_for_keywords(query, keywords)

        query = self._filter_for_wildcard(query, code)

        return query

    def _filter_for_release(self, query, since):
        if since is not None:
            query = query.add_column(Release.effective_date)

            for date in since:
                query = query.filter(Release.effective_date >= date)

        else:
            query = query.filter(ClinicianDescriptor.deleted == False)

        return query

    @classmethod
    def _filter_for_keywords(cls, query, keywords):
        filter_conditions = [(ClinicianDescriptor.descriptor.ilike('%{}%'.format(word))) for word in keywords]

        return query.filter(or_(*filter_conditions))

    @classmethod
    def _filter_for_wildcard(cls, query, codes):
        filter_condition = []
        if codes is not None:

            for code in codes:
                code = code.split('*')
                prefix = code[0]
                suffix = code[1]

                filter_condition.append(and_(ClinicianDescriptorCodeMapping.code.like(f'{prefix}%'),
                                             ClinicianDescriptorCodeMapping.code.ilike(f'%{suffix}')))

            query = query.filter(or_(*filter_condition))

        return query
