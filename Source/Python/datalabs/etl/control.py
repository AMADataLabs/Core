""" Archival Transformer classes. """
from   dataclasses import dataclass
import logging

from datalabs.etl.transform import TransformerTask
from   datalabs.parameter import add_schema

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class DAGNotificationFactoryParameters:
    data: object
    execution_time: str = None


class DAGNotificationFactoryTask(TransformerTask):
    PARAMETER_CLASS = DAGNotificationFactoryParameters

    def _transform(self):
        pass
