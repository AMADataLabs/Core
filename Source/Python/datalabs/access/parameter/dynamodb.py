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
        if environment is None:
            environment = os.environ
        global_variables = self._get_parameters_from_dynamodb("GLOBAL")

        parameters = self._get_parameters_from_dynamodb(self._parameters.task)

        ReferenceEnvironmentLoader(global_variables).load(environment=parameters)

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

    def _get_parameters_from_dynamodb(self, task):
        key=dict(
            DAG=dict(S=self._parameters.dag),
            Task=dict(S=task)
        )
        response = None

        LOGGER.debug('GetItem from table: %s', self._parameters.table)
        LOGGER.debug('GetItem key: %s', key)

        with AWSClient("dynamodb") as dynamodb:
            response = dynamodb.get_item(
                TableName=self._parameters.table,
                Key=key
            )

        return self._extract_parameters(response)

    @classmethod
    def _extract_parameters(cls, response):
        parameters = {}

        if "Item" in response:
            if "Variables" not in response["Item"]:
                raise ValueError(f'Invalid DynamoDB configuration item: {json.dumps(response)}')

            parameters = json.loads(response["Item"]["Variables"]["S"])

        return parameters


class DynamoDBTaskParameterGetterMixin:
    # pylint: disable=redefined-outer-name
    @classmethod
    def _get_dag_task_parameters_from_dynamodb(cls, dag: str, task: str):
        dynamodb_loader = DynamoDBEnvironmentLoader(dict(
            table=os.environ["DYNAMODB_CONFIG_TABLE"],
            dag=dag,
            task=task
        ))
        parameters = {}

        dynamodb_loader.load(environment=parameters)

        return parameters
