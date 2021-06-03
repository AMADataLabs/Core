""" AWS S3 Loader """
from   dataclasses import dataclass
import logging

from   datalabs.access.aws import AWSClient
from   datalabs.etl.load import LoaderTask
from   datalabs.parameter import add_schema

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class SNSLoaderParameters:
    topic: str
    data: object
    endpoint_url: str = None
    access_key: str = None
    secret_key: str = None
    region_name: str = None


class SNSLoaderLoaderTask(LoaderTask):
    PARAMETER_CLASS = SNSLoaderParameters

    def _get_client(self):
        return AWSClient(
            'sns',
            endpoint_url=self._parameters.endpoint_url,
            aws_access_key_id=self._parameters.access_key,
            aws_secret_access_key=self._parameters.secret_key,
            region_name=self._parameters.region_name
        )

    def _load(self):
        # implement
        pass
