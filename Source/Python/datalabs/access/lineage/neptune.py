"""Neptune lineage class"""
import logging
import os

from   neptune_python_utils.gremlin_utils import GremlinUtils

from   datalabs.access.credentials import Credentials
from   datalabs.access.lineage.base import Configuration, LineageLogger

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=abstract-method
class NeptuneLineageLogger(LineageLogger):
    def __init__(self, configuration: Configuration = None, credentials: Credentials = None, key: str = None):
        super().__init__(credentials, key)

        self._configuration = self._load_or_verify_configuration(configuration, self._key)

    def connect(self):
        os.environ['NEPTUNE_CLUSTER_ENDPOINT'] = self._configuration.host
        os.environ['NEPTUNE_CLUSTER_PORT'] = str(self._configuration.port)
        GremlinUtils.init_statics(globals())
        gremlin_utils = GremlinUtils()
        self._connection = gremlin_utils.remote_connection()

    @classmethod
    def _load_or_verify_configuration(cls, configuration: Configuration, key: str):
        if configuration is None:
            configuration = Configuration.load(key)
        elif not hasattr(configuration, 'host'):
            raise ValueError('Invalid configuration object.')

        return configuration
