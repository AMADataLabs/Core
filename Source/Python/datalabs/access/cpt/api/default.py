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


class DefaultEndpointTask(APIEndpointTask):
    def _run(self, session):
        raise ResourceNotFound('Bad endpoint path')
