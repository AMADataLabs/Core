""" AWS S3 Loader """
from   dataclasses import dataclass
import logging

from   datalabs.etl.task import ExecutionTimeMixin
from   datalabs.parameter import add_schema

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class SignedPDFTransformerParameters:
    pass


class SignedPDFTransformerTask(ExecutionTimeMixin):
    PARAMETER_CLASS = SignedPDFTransformerParameters
