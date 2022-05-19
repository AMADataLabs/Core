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
    base_path: str
    credentials_file: str
    credentials_password: str
    recipient: str
    data: object
    execution_time: str=None


class SignedPDFTransformerTask(ExecutionTimeMixin):
    PARAMETER_CLASS = SignedPDFTransformerParameters
