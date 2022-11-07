"""Neptune lineage class"""
from   dataclasses import dataclass
import logging
import os

from   neptune_python_utils.gremlin_utils import GremlinUtils

from   datalabs.access.lineage.base import LineageLogger
from   datalabs.parameter import add_schema

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class NeptuneParameters:
    host: str
    port: str="8182"


# pylint: disable=abstract-method
class NeptuneLineageLogger(LineageLogger):
    PARAMETER_CLASS = NeptuneParameters

    def connect(self):
        os.environ['NEPTUNE_CLUSTER_ENDPOINT'] = self._parameters.host
        os.environ['NEPTUNE_CLUSTER_PORT'] = str(self._parameters.port)

        GremlinUtils.init_statics(globals())

        gremlin_utils = GremlinUtils()

        self._connection = gremlin_utils.remote_connection()
