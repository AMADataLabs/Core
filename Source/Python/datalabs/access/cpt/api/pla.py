from   abc import abstractmethod
from   collections import defaultdict
import json
import logging
import os

from   sqlalchemy import or_
from   sqlalchemy.orm.exc import NoResultFound

from   datalabs.access.task import APIEndpointTask, APIEndpointException, InvalidRequest, ResourceNotFound
import datalabs.etl.cpt.dbmodel as dbmodel

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class BasePLADetailsEndpointTask(APIEndpointTask):
    LENGTH_MODEL_NAMES = dict(short='PLAShortDescriptor', medium='PLAMediumDescriptor', long='PLALongDescriptor')

    def _run(self, session):
        LOGGER.debug('Parameters: %s', self._parameters)
        self._set_parameter_defaults()
        LOGGER.debug('Parameters: %s', self._parameters)

        lengths = self._parameters.query.get('length')

        if not self._lengths_are_valid(lengths):
            raise InvalidRequest("Invalid query parameter")

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
            dbmodel.PLACode,
            dbmodel.PLALongDescriptor,
            dbmodel.PLAMediumDescriptor,
            dbmodel.PLAShortDescriptor,
            # dbmodel.Release,
            dbmodel.Manufacturer,
            dbmodel.Lab
        ).join(
            dbmodel.PLALongDescriptor,
            dbmodel.PLAMediumDescriptor,
            dbmodel.PLAShortDescriptor,
        # ).join(
        #     dbmodel.ReleasePLACodeMapping,
        #     dbmodel.ReleasePLACodeMapping.code==dbmodel.PLACode.code
        # ).join(
        #     dbmodel.Release,
        #     dbmodel.Release.id==dbmodel.ReleasePLACodeMapping.release
        ).join(
            dbmodel.ManufacturerPLACodeMapping,
            dbmodel.ManufacturerPLACodeMapping.code==dbmodel.PLACode.code
        ).join(
            dbmodel.Manufacturer,
            dbmodel.Manufacturer.id==dbmodel.ManufacturerPLACodeMapping.manufacturer
        ).join(
            dbmodel.LabPLACodeMapping,
            dbmodel.LabPLACodeMapping.code==dbmodel.PLACode.code
        ).join(
            dbmodel.Lab,
            dbmodel.Lab.id==dbmodel.LabPLACodeMapping.lab
        )
        return query

    @abstractmethod
    def _filter(self, query):
        pass

    @classmethod
    def _generate_response_body(cls, rows, lengths):
        body = []

        for row in rows:
            row_body = dict(
                code=row.PLACode.code,
                code_status=row.PLACode.status,
                # publish_date=row.Release.publish_date,
                # effective_date=row.Release.effective_date,
                test_name=row.PLACode.test_name,
                lab_name=row.Lab.name,
                manufacturer_name=row.Manufacturer.name
            )

            for length in lengths:
                row_body.update({length + '_descriptor': getattr(row, cls.LENGTH_MODEL_NAMES[length]).descriptor})

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

        return self._filter_by_code(query, code)

    @classmethod
    def _filter_by_code(cls, query, code):
        return query.filter(dbmodel.PLACode.code == code)


class AllPLADetailsEndpointTask(BasePLADetailsEndpointTask):
    def _filter(self, query):
        since = self._parameters.query.get('since')
        keywords = self._parameters.query.get('keyword')
        lengths = self._parameters.query.get('length')

        query = self._filter_for_release(query, since)

        query = self._filter_for_keywords(query, keywords, lengths)

        return query

    def _filter_for_release(self, query, since):
        if since is not None:
            query = query.add_column(Release.effective_date)

            for date in query_parameter['since']:
                query = query.filter(Release.effective_date >= date)

        return query

    def _filter_for_keywords(self, query, keywords, lengths):
        length_dict = {length:getattr(dbmodel, 'PLA'+length.capitalize()+'Descriptor') for length in lengths}
        filter_conditions = []

        for length in lengths:
            filter_conditions = [(length_dict.get(length).descriptor.ilike('%{}%'.format(word))) for word in keywords]

        return query.filter(or_(*filter_conditions))
