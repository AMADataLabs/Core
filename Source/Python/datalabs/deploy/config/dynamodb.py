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
        parameters = dict(
            TableName=self._table, FilterExpression="Task = :task", ExpressionAttributeValues={":task": {"S": "DAG"}}
        )

        return set(self._paginated_scan(self._aggregate_dags, parameters))

    def get_apis(self) -> Iterable[str]:
        parameters = dict(
            TableName=self._table, FilterExpression="Task = :task", ExpressionAttributeValues={":task": {"S": "ROUTE"}}
        )

        return set(self._paginated_scan(self._aggregate_dags, parameters))

    def get_tasks(self, dag: str):
        parameters = dict(
            TableName=self._table, FilterExpression="DAG = :dag", ExpressionAttributeValues={":dag": {"S": dag}}
        )

        return set(self._paginated_scan(self._aggregate_tasks, parameters))

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

    @classmethod
    def _paginated_scan(cls, aggregation_function, parameters):
        aggregate = []

        with AWSClient("dynamodb") as dynamodb:
            response = dynamodb.scan(**parameters)

            aggregation_function(aggregate, response["Items"])

            while "LastEvaluatedKey" in response:
                parameters["ExclusiveStartKey"] = response["LastEvaluatedKey"]

                response = dynamodb.scan(**parameters)

                aggregation_function(aggregate, response["Items"])

        return aggregate

    @classmethod
    def _aggregate_dags(cls, dags: list[str], items: Iterable[dict]):
        dags.extend([item["DAG"]["S"] for item in items])

    @classmethod
    def _aggregate_tasks(cls, tasks: list[str], items: Iterable[dict]):
        for item in items:
            task = item["Task"]["S"]

            if task not in ["DAG", "GLOBAL"]:
                tasks.append(task)
