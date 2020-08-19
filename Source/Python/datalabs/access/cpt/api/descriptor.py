""" CPT Descriptor endpoint classes. """
from   abc import abstractmethod
import logging

from   sqlalchemy import or_

from   datalabs.access.task.api import APIEndpointTask, InvalidRequest, ResourceNotFound
import datalabs.etl.cpt.dbmodel as dbmodel

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class BaseDescriptorEndpointTask(APIEndpointTask):
    LENGTH_MODEL_NAMES = dict(short='ShortDescriptor', medium='MediumDescriptor', long='LongDescriptor')

    def _run(self, session):
        LOGGER.debug('Parameters: %s', self._parameters)
        self._set_parameter_defaults()
        LOGGER.debug('Parameters: %s', self._parameters)

        lengths = self._parameters.query.get('length')

        if not self._lengths_are_valid(lengths):
            raise InvalidRequest(f"Invalid query parameter: length={lengths}")

        query = self._query_for_descriptors(session)

        query = self._filter(query)

        self._response_body = self._generate_response_body(query.all(), lengths)

    def _set_parameter_defaults(self):
        self._parameters.query['length'] = self._parameters.query.get('length') or ['short', 'medium', 'long']
        self._parameters.query['keyword'] = self._parameters.query.get('keyword') or []

    @classmethod
    def _lengths_are_valid(cls, lengths):
        return all(length in cls.LENGTH_MODEL_NAMES.keys() for length in lengths)

    @classmethod
    def _query_for_descriptors(cls, session):
        query = session.query(
            dbmodel.Code,
            dbmodel.LongDescriptor,
            dbmodel.MediumDescriptor,
            dbmodel.ShortDescriptor
        ).join(
            dbmodel.LongDescriptor,
            dbmodel.MediumDescriptor,
            dbmodel.ShortDescriptor
        )

        return query

    @abstractmethod
    def _filter(self, query):
        pass

    @classmethod
    def _generate_response_body(cls, rows, lengths):
        body = []

        for row in rows:
            row_body = dict(code=row.Code.code)

            for length in lengths:
                row_body.update({length + '_descriptor': getattr(row, cls.LENGTH_MODEL_NAMES[length]).descriptor})

            body.append(row_body)

        return body


class DescriptorEndpointTask(BaseDescriptorEndpointTask):
    def _run(self, session):
        super()._run(session)

        if not self._response_body:
            raise ResourceNotFound('No descriptor found for the given CPT Code')

        self._response_body = self._response_body[0]

    def _filter(self, query):
        code = self._parameters.path.get('code')

        return self._filter_by_code(query, code)

    @classmethod
    def _filter_by_code(cls, query, code):
        return query.filter(dbmodel.Code.code == code)


class AllDescriptorsEndpointTask(BaseDescriptorEndpointTask):
    def _filter(self, query):
        since = self._parameters.query.get('since')
        keywords = self._parameters.query.get('keyword')
        lengths = self._parameters.query.get('length')

        query = self._filter_for_release(query, since)

        query = self._filter_for_keywords(query, keywords, lengths)

        return query

    @classmethod
    def _filter_for_release(cls, query, since):
        if since is not None:
            query = query.add_column(dbmodel.Release.effective_date)

            for date in since:
                query = query.filter(dbmodel.Release.effective_date >= date)

        return query

    @classmethod
    def _filter_for_keywords(cls, query, keywords, lengths):
        length_dict = {length:getattr(dbmodel, length.capitalize()+'Descriptor') for length in lengths}
        filter_conditions = []

        for length in lengths:
            filter_conditions += [(length_dict.get(length).descriptor.ilike('%{}%'.format(word))) for word in keywords]

        return query.filter(or_(*filter_conditions))
