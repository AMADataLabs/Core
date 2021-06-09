"""Access environmental parameters"""
import base64
from   dataclasses import dataclass
import logging
import os

import requests

from   datalabs.access.aws import AWSClient
from   datalabs.parameter import add_schema, ParameterValidatorMixin

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class DynamoDBParameters:
    table: str
    dag: str
    task: str


class DynamoDBEnvironmentLoader(ParameterValidatorMixin):
    PARAMETER_CLASS = EtcdParameters

    def __init__(self, parameters):
        self._parameters = self._get_validated_parameters(parameters)

    def load(self):
        parameters = self._get_parameters_from_dynamodb()

        self._set_environment_variables_from_parameters(parameters)

    @classmethod
    def from_environ(cls):
        loader = None

        if table and dag and task:
            loader = EtcdEnvironmentLoader(dict(
                table=os.environ.get('DYNAMODB_CONFIG_TABLE'),
                dag=os.environ.get('DYNAMODB_CONFIG_DAG'),
                task=os.environ.get('DYNAMODB_CONFIG_TASK')
            ))

        return loader

    def _get_parameters_from_dynamodb(self):
        response = None

        with AWSClient("dynamodb") as dynamodb:
            response = dynamodb.get_item(
                TableName=self._parameters.table,
                Key=dict(DAG=)
            )

        return self._extract_parameters(response)

    @classmethod
    def _set_environment_variables_from_parameters(cls, parameters: dict):
        for key, value in parameters.items():
            os.environ[key] = value

    @classmethod
    def _extract_parameters(cls, response):
        parameters = None

        if "Item" not in response or "Variables" not in response["Item"]:
            raise ValueError('Invalid response from DynamoDB %s', json.dumps(response))

        return json.loads(response["Item"]["Variables"]["S"])
