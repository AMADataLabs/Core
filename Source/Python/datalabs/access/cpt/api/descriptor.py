""" CPT Descriptor endpoint classes. """
from   abc import abstractmethod
from   dataclasses import dataclass
import logging

from   sqlalchemy import or_

from   datalabs.access.api.task import APIEndpointTask, InvalidRequest, ResourceNotFound
from   datalabs.access.cpt.api.filter import ReleaseFilterMixin, WildcardFilterMixin
import datalabs.model.cpt.api as dbmodel
from   datalabs.access.cpt.api import languages
from   datalabs.access.orm import Database
from   datalabs.parameter import add_schema

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=too-many-instance-attributes
@add_schema(unknowns=True)
@dataclass
class DescriptorEndpointParameters:
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


class BaseDescriptorEndpointTask(APIEndpointTask):
    PARAMETER_CLASS = DescriptorEndpointParameters
    LENGTH_MODEL_NAMES = dict(short='ShortDescriptor', medium='MediumDescriptor', long='LongDescriptor')

    def run(self):
        LOGGER.debug('Parameters: %s', self._parameters)

        with Database.from_parameters(self._parameters) as database:
            self._run(database)


    def _run(self, database):
        self._set_parameter_defaults()
        LOGGER.debug('Parameters: %s', self._parameters)

        lengths = self._parameters.query.get('length')
        language = self._parameters.query.get('language').lower()

        if not isinstance(lengths, list):
            lengths = [lengths]

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

        for row in rows:
            row_body = dict(code=row.Code.code)

            for length in lengths:
                row_body.update({"language": language.lower()})
                descriptor = getattr(row, cls.LENGTH_MODEL_NAMES[length.lower()])
                descriptor = getattr(descriptor, "descriptor" + languages.Descriptor_Suffix[language])
                row_body.update({length.lower() + '_descriptor': descriptor})
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

        # pylint: disable=singleton-comparison
        return query.filter(dbmodel.Code.deleted == False)

    @classmethod
    def _filter_for_keywords(cls, query, keywords, lengths):
        length_dict = {length:getattr(dbmodel, length.capitalize()+'Descriptor') for length in lengths}
        filter_conditions = []

        for length in lengths:
            filter_conditions += [(length_dict.get(length).descriptor.ilike('%{}%'.format(word))) for word in keywords]

        return query.filter(or_(*filter_conditions))
