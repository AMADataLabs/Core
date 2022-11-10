""" Lineage """
from   abc import abstractmethod
import logging

from   datalabs.access.datastore import Datastore

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class LineageLogger(Datastore):
    # pylint: disable=redefined-builtin
    @abstractmethod
    def log(self, parent_uri, child_uri, type=None):
        pass


class LineageException(Exception):
    pass


def register_logger(key: str, logger_class: LineageLogger):
    LOGGERS[key.upper()] = logger_class


def get_logger(key: str, parameters: dict):
    key = key.upper()

    if key not in LOGGERS:
        raise LineageException(f"No Lineage Logger registered for key '{key}'.")

    return LOGGERS[key](parameters)


LOGGERS = {}
