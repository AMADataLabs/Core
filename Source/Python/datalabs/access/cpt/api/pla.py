""" PLA Details endpoints. """
from   abc import abstractmethod
import logging

from   sqlalchemy import or_, and_

from   datalabs.access.api.task import APIEndpointTask, ResourceNotFound
import datalabs.model.cpt.api as dbmodel

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class BasePLADetailsEndpointTask(APIEndpointTask):
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
        query = session.query(
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
    def _run(self, session):
        super()._run(session)

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


class AllPLADetailsEndpointTask(BasePLADetailsEndpointTask):
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
            query = query.add_column(dbmodel.Release.effective_date)

            for date in since:
                query = query.filter(dbmodel.Release.effective_date >= date)

        else:
            query = query.filter(dbmodel.PLADetails.status == 'EXISTING')

        return query

    @classmethod
    def _filter_for_keywords(cls, query, keywords):
        filter_conditions = [dbmodel.PLADetails.test_name.ilike('%{}%'.format(word)) for word in keywords]
        filter_conditions += [dbmodel.Manufacturer.name.ilike('%{}%'.format(word)) for word in keywords]
        filter_conditions += [dbmodel.Lab.name.ilike('%{}%'.format(word)) for word in keywords]

        return query.filter(or_(*filter_conditions))

    @classmethod
    def _filter_for_wildcard(cls, query, codes):
        filter_condition = []

        if codes is not None:
            for code in codes:
                code = code.split('*')
                prefix = code[0]
                suffix = code[1]

                filter_condition.append(and_(dbmodel.PLADetails.code.like(f'{prefix}%'),
                                             dbmodel.PLADetails.code.ilike(f'%{suffix}')))

            query = query.filter(or_(*filter_condition))

        return query
