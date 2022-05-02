""" AWS S3 Loader """
from   dataclasses import dataclass
import logging

from   datalabs.access.aws import AWSClient
from   datalabs.etl.task import ExecutionTimeMixin
from   datalabs.parameter import add_schema

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class SignedPDFTransformerTask(ExecutionTimeMixin):
    pass
