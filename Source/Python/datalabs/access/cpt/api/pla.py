""" PLA Details endpoints. """
from   abc import abstractmethod
import logging

from   datalabs.access.api.task import APIEndpointTask, ResourceNotFound
from   datalabs.access.cpt.api.filter import KeywordFilterMixin, WildcardFilterMixin
import datalabs.model.cpt.api as dbmodel

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class BasePLADetailsEndpointTask(APIEndpointTask):
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
        query = database.query(
            dbmodel.PLADetails,
            dbmodel.Manufacturer,
            dbmodel.Lab
        ).join(
        ).join(
            dbmodel.ManufacturerPLACodeMapping,
            dbmodel.ManufacturerPLACodeMapping.code == dbmodel.PLADetails.code
        ).join(
            dbmodel.Manufacturer,
            dbmodel.Manufacturer.id == dbmodel.ManufacturerPLACodeMapping.manufacturer
        ).join(
            dbmodel.LabPLACodeMapping,
            dbmodel.LabPLACodeMapping.code == dbmodel.PLADetails.code
        ).join(
            dbmodel.Lab,
            dbmodel.Lab.id == dbmodel.LabPLACodeMapping.lab
        )
        return query

    @abstractmethod
    def _filter(self, query):
        pass

    @classmethod
    def _generate_response_body(cls, rows):
        body = []

        for row in rows:
            row_body = dict(
                code=row.PLADetails.code,
                test=row.PLADetails.test_name,
                lab=row.Lab.name,
                manufacturer=row.Manufacturer.name
            )

            body.append(row_body)

        return body


class PLADetailsEndpointTask(BasePLADetailsEndpointTask):
    def _run(self, database):
        super()._run(database)

        if not self._response_body:
            raise ResourceNotFound('No PLA details found for the given PLA code')

        self._response_body = self._response_body[0]

    def _filter(self, query):
        code = self._parameters.path.get('code')
        query = self._filter_by_code(query, code)

        return query.filter(dbmodel.PLADetails.status == 'EXISTING')

    @classmethod
    def _filter_by_code(cls, query, code):
        return query.filter(dbmodel.PLADetails.code == code)


# pylint: disable=too-many-ancestors
class AllPLADetailsEndpointTask(BasePLADetailsEndpointTask, KeywordFilterMixin, WildcardFilterMixin):
    def _filter(self, query):
        since = self._parameters.query.get('since')
        keywords = self._parameters.query.get('keyword')
        code = self._parameters.query.get('code')
        keyword_fields = [dbmodel.PLADetails.test_name, dbmodel.Manufacturer.name, dbmodel.Lab.name]

        query = self._filter_for_release(query, since)

        query = self._filter_for_keywords(keyword_fields, query, keywords)

        query = self._filter_for_wildcard(dbmodel.PLADetails, query, code)

        return query

    @classmethod
    def _filter_for_release(cls, query, since):
        if since is not None:
            query = query.add_column(dbmodel.Release.effective_date)

            for date in since:
                query = query.filter(dbmodel.Release.effective_date >= date)

        else:
            query = query.filter(dbmodel.PLADetails.status == 'EXISTING')

        return query
