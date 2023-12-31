""" AWS S3 Loader """
from   dataclasses import dataclass
import json
import logging

from   datalabs.access.aws import AWSClient
from   datalabs.parameter import add_schema
from   datalabs.task import Task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class SNSMessageLoaderParameters:
    topic_arn: str
    execution_time: str = None
    endpoint_url: str = None
    access_key: str = None
    secret_key: str = None
    region_name: str = None


class SNSMessageLoaderTask(Task):
    PARAMETER_CLASS = SNSMessageLoaderParameters

    def run(self):
        with AWSClient(
            'sns',
            endpoint_url=self._parameters.endpoint_url,
            aws_access_key_id=self._parameters.access_key,
            aws_secret_access_key=self._parameters.secret_key,
            region_name=self._parameters.region_name
        ) as sns:
            for message in json.loads(self._data[0].decode()):
                LOGGER.info('Publishing the following message to %s: %s', self._parameters.topic_arn, message)
                sns.publish(
                    TargetArn=self._parameters.topic_arn,
                    Message=json.dumps(message)
                )
