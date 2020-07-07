from   collections import defaultdict
import json
import os

from   sqlalchemy import create_engine
from   sqlalchemy.orm import sessionmaker

from   datalabs.access.task import APIEndpointTask, APIEndpointException, InvalidRequest, ResourceNotFound
from   datalabs.etl.cpt.dbmodel import Code, ShortDescriptor, LongDescriptor, MediumDescriptor
from   datalabs.access.database import Database


class DescriptorEndpointTask(APIEndpointTask):
    LENGTH_MODEL_NAMES = dict(short='ShortDescriptor', medium='MediumDescriptor', long='LongDescriptor')

    def _run(self, session):
        code = self._parameters.path.get('code')
        lengths = self._paramters.query.get('length') or ['short', 'medium', 'long']

        if not cls._lengths_are_valid(lengths):
            raise InvalidRequest("Invalid query parameter")

        query = self._query_for_descriptor(session, code)

        if query is None:
            raise ResourceNotFound('No descriptor found for the given CPT Code')

        self._status_code, self._response_body = cls._generate_response_body(query.one(), lengths)

    @classmethod
    def _lengths_are_valid(cls, lengths):
        return all(length in cls.LENGTH_MODEL_NAMES.keys() for length in lengths)

    @classmethod
    def _query_for_descriptor(cls, session, code):
        query = None

        if code is not None:
            query = session.query(Code, LongDescriptor, MediumDescriptor, ShortDescriptor).join(
                LongDescriptor, MediumDescriptor, ShortDescriptor
            )
            query = query.filter(Code.code == code)

        return query

    @classmethod
    def _generate_response_body(cls, row, lengths):
        body = dict(code=row.Code.code)

        for length in lengths:
            body.update({length + '_descriptor': getattr(row, cls.LENGTH_MODEL_NAMES[length]).descriptor})

        return body
