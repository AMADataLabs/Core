from   abc import abstractmethod
from   collections import defaultdict
import json
import logging
import os

from   sqlalchemy import or_
from   sqlalchemy.orm.exc import NoResultFound

from   datalabs.access.task import APIEndpointTask, APIEndpointException, InvalidRequest, ResourceNotFound
from   datalabs.etl.cpt.dbmodel import Release

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class ReleasesEndpointTask(APIEndpointTask):
    def _run(self, session):
        self._set_parameter_defaults()

        max_results = self._parameters.query.get('results')
        if not self._max_results_is_valid(max_results):
            raise InvalidRequest(f'Invalid query parameter: results={max_results}')

        query = self._query_for_releases(session)

        query = self._filter_for_max_results(query)

        self._response_body = self._generate_response_body(query.all())

    def _set_parameter_defaults(self):
        if self._parameters.query['results'] is not None and not hasattr(self._parameters.query['results'], 'isdigit'):
            self._parameters.query['results'] = self._parameters.query.get('results')[0]

        self._parameters.query['keyword'] = self._parameters.query.get('keyword') or []

    @classmethod
    def _max_results_is_valid(cls, max_results):
        valid = False

        if max_results and max_results.isdigit() and int(max_results) > 0:
            valid = True
        elif max_results is None:
            valid = True

        return valid

    @classmethod
    def _query_for_releases(cls, session):
        return session.query(Release)

    def _filter_for_max_results(self, query):
        max_results = self._parameters.query.get('results')

        if max_results is not None:
            query = query.limit(max_results)

        return query

    @classmethod
    def _generate_response_body(cls, rows):
        return [
            dict(
                id=row.id,
                publish_date=str(row.publish_date),
                effective_date=str(row.effective_date),
                type=row.type
            )
         for row in rows]
