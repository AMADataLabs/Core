""" Tool for loading Kubernetes ConfigMap data into DynamoDB. """
import logging
import pprint
from typing import Iterable

from datalabs.access.aws import AWSClient
from datalabs.access.parameter.file import ParameterExtractorMixin

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class ConfigMapLoader(ParameterExtractorMixin):
    def __init__(self, table: str):
        self._table = table

    def load(self, filenames, dry_run=False):
        dag, variables = self._extract_variables_from_config(filenames)

        parameters = self._parse_variables(variables)

        parameters = self._expand_macros(parameters)

        if dry_run:
            LOGGER.info("Parameters:\n%s", pprint.pformat(parameters))
        else:
            self._load_variables(dag, parameters)

    def _load_variables(self, dag, parameters):
        with AWSClient("dynamodb") as dynamodb:
            for task, task_variables in parameters.items():
                self._load_variables_into_dynamodb(dynamodb, dag, task, task_variables)

    def _load_variables_into_dynamodb(self, dynamodb, dag, task, variables):
        response = None
        item = self._generate_item(dag, task, variables)

        response = dynamodb.put_item(TableName=self._table, Item=item)

        return response


class IncompleteConfigurationException(Exception):
    pass


class Configuration:
    def __init__(self, table: str):
        self._table = table

    def get_dags(self) -> Iterable[str]:
        dags = set()

        with AWSClient("dynamodb") as dynamodb:
            response = dynamodb.scan(TableName=self._table)

        for item in response["Items"]:
            dags.add(item["DAG"]["S"])

        return dags

    def get_tasks(self, dag: str):
        tasks = []

        parameters = dict(
            TableName=self._table, FilterExpression="DAG = :dag", ExpressionAttributeValues={":dag": {"S": dag}}
        )

        with AWSClient("dynamodb") as dynamodb:
            response = dynamodb.scan(**parameters)

        for item in response["Items"]:
            task = item["Task"]["S"]

            if task not in ["DAG", "GLOBAL"]:
                tasks.append(task)

        return tasks

    def clear_dag(self, dag: str):
        parameters = dict(
            TableName=self._table, FilterExpression="DAG = :dag", ExpressionAttributeValues={":dag": {"S": dag}}
        )

        with AWSClient("dynamodb") as dynamodb:
            response = dynamodb.scan(**parameters)

            for item in response["Items"]:
                dynamodb.delete_item(
                    TableName=self._table,
                    Key={"DAG": {"S": dag}, "Task": {"S": item["Task"]["S"]}},
                )
