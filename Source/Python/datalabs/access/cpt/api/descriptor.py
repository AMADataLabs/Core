""" CPT Descriptor endpoint classes. """
from   abc import abstractmethod
import logging

from   sqlalchemy import or_
from   sqlalchemy.orm import defer, undefer

from   datalabs.access.api.task import APIEndpointTask, InvalidRequest, ResourceNotFound
from   datalabs.access.cpt.api.filter import ReleaseFilterMixin, WildcardFilterMixin
import datalabs.model.cpt.api as dbmodel
from datalabs.access.cpt.api import languages

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class BaseDescriptorEndpointTask(APIEndpointTask):
    LENGTH_MODEL_NAMES = dict(short='ShortDescriptor', medium='MediumDescriptor', long='LongDescriptor')

    def _run(self, database):
        LOGGER.debug('Parameters: %s', self._parameters)
        self._set_parameter_defaults()
        LOGGER.debug('Parameters: %s', self._parameters)

        lengths = self._parameters.query.get('length')
        language = self._parameters.query.get('language').lower()

        if not self._lengths_are_valid(lengths):
            raise InvalidRequest(f"Invalid query parameter: length={lengths}")
        if not self._language_is_valid(language):
            raise InvalidRequest(f"Invalid query parameter: language={language}")

        query = self._query_for_descriptors(database)

        query = self._filter(query)

        self._response_body = self._generate_response_body(query.all(), lengths, language)

    def _set_parameter_defaults(self):
        self._parameters.query['length'] = self._parameters.query.get('length') or ['short', 'medium', 'long']
        self._parameters.query['keyword'] = self._parameters.query.get('keyword') or []
        self._parameters.query['language'] = self._parameters.query.get('language') or 'english'

    @classmethod
    def _lengths_are_valid(cls, lengths):
        if type(lengths) is not list:
            lengths = [lengths]
        return all(length in cls.LENGTH_MODEL_NAMES.keys() for length in lengths)

    @classmethod
    def _language_is_valid(cls, language):
        return language in languages.Descriptor_Languages

    @classmethod
    def _query_for_descriptors(cls, database):
        query = database.query(
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
    def _generate_response_body(cls, rows, lengths, language):
        body = []

        if type(lengths) is not list:
            lengths = [lengths]

        for row in rows:
            row_body = dict(code=row.Code.code)

            for length in lengths:
                row_body.update({"language": language.lower()})
                if language == 'chinese':
                    row_body.update({length.lower() + '_descriptor': getattr(row, cls.LENGTH_MODEL_NAMES[length.lower()]).descriptor_chinese})
                elif language == 'spanish':
                    row_body.update({length.lower() + '_descriptor': getattr(row, cls.LENGTH_MODEL_NAMES[length.lower()]).descriptor_spanish})
                else:
                    row_body.update({length.lower() + '_descriptor': getattr(row, cls.LENGTH_MODEL_NAMES[length.lower()]).descriptor})

            body.append(row_body)

        return body


class DescriptorEndpointTask(BaseDescriptorEndpointTask):
    def _run(self, database):
        super()._run(database)

        if not self._response_body:
            raise ResourceNotFound('No descriptor found for the given CPT Code')

        self._response_body = self._response_body[0]

    def _filter(self, query):
        code = self._parameters.path.get('code')
        query = self._filter_by_code(query, code)

        # pylint: disable=singleton-comparison
        return query.filter(dbmodel.Code.deleted == False)

    @classmethod
    def _filter_by_code(cls, query, code):
        return query.filter(dbmodel.Code.code == code)


# pylint: disable=too-many-ancestors
class AllDescriptorsEndpointTask(BaseDescriptorEndpointTask, ReleaseFilterMixin, WildcardFilterMixin):
    def _filter(self, query):
        since = self._parameters.query.get('since')
        keywords = self._parameters.query.get('keyword')
        lengths = self._parameters.query.get('length')
        code = self._parameters.query.get('code')

        query = self._filter_for_release(dbmodel.Code, query, since)

        query = self._filter_for_keywords(query, keywords, lengths)

        query = self._filter_for_wildcard(dbmodel.Code, query, code)

        return query

    @classmethod
    def _filter_for_keywords(cls, query, keywords, lengths):
        length_dict = {length:getattr(dbmodel, length.capitalize()+'Descriptor') for length in lengths}
        filter_conditions = []

        for length in lengths:
            filter_conditions += [(length_dict.get(length).descriptor.ilike('%{}%'.format(word))) for word in keywords]

        return query.filter(or_(*filter_conditions))
