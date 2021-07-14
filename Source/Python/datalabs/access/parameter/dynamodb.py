"""Access environmental parameters"""
from   dataclasses import dataclass
import json
import logging
import os

from   datalabs.access.aws import AWSClient
from   datalabs.access.parameter.system import ReferenceEnvironmentLoader
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
    PARAMETER_CLASS = DynamoDBParameters

    def __init__(self, parameters):
        self._parameters = self._get_validated_parameters(parameters)

    def load(self, environment: dict = None):
        environment = environment or os.environ
        parameters = self._get_parameters_from_dynamodb()

        ReferenceEnvironmentLoader(parameters).load(environment=parameters)

        environment.update(parameters)

    @classmethod
    def from_environ(cls):
        table = os.environ.get('DYNAMODB_CONFIG_TABLE')
        dag = os.environ.get('DYNAMODB_CONFIG_DAG')
        task = os.environ.get('DYNAMODB_CONFIG_TASK')
        loader = None

        if table and dag and task:
            loader = DynamoDBEnvironmentLoader(dict(table=table, dag=dag, task=task))

        return loader

    def _get_parameters_from_dynamodb(self):
        response = None

        with AWSClient("dynamodb") as dynamodb:
            response = dynamodb.get_item(
                TableName=self._parameters.table,
                Key=dict(
                    DAG=dict(S=self._parameters.dag),
                    Task=dict(S=self._parameters.task)
                )
            )

        return self._extract_parameters(response)

    @classmethod
    def _extract_parameters(cls, response):
        if "Item" not in response or "Variables" not in response["Item"]:
            raise ValueError(f'Invalid response from DynamoDB {json.dumps(response)}')

        return json.loads(response["Item"]["Variables"]["S"])
