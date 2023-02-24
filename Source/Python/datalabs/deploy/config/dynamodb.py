""" Tool for loading Kubernetes ConfigMap data into DynamoDB. """
import json
import logging
import pprint

import yaml

from   datalabs.access.aws import AWSClient
from   datalabs.access.environment import VariableTree
from   datalabs.plugin import import_plugin

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class ConfigMapLoader:
    def __init__(self, table: str):
        self._table = table

    def load(self, filenames, dry_run=False):
        variables = self._extract_variables_from_config(filenames)

        dag, parameters = self._parse_variables(variables)

        parameters = self._expand_macros(parameters)

        if dry_run:
            LOGGER.info("Parameters:\n%s", pprint.pformat(parameters))
        else:
            self._load_variables(dag, parameters)

    @classmethod
    def _extract_variables_from_config(cls, filenames):
        config = {}

        for filename in filenames:
            with open(filename, encoding='utf-8') as file:
                config.update(yaml.safe_load(file.read())['data'])

        for key, value in config.items():
            if not key.endswith('@MACRO_COUNT@') and not isinstance(value, str):
                raise ValueError(f'The value for parameter {key} is not a string, but is {type(value)}: {value}.')

        return config

    def _parse_variables(self, variables):
        parameters = {}
        var_tree = VariableTree.generate(variables)
        dag = self._get_dag_id(var_tree)
        parameters["GLOBAL"] = self._get_global_variables(dag, var_tree)
        tasks = var_tree.get_branches([dag])

        for task in tasks:
            parameters[task] = var_tree.get_branch_values([dag, task])

        return (dag, parameters)

    @classmethod
    def _expand_macros(cls, parameters):
        parameters = cls._expand_task_parameters(parameters)

        if "DAG" in parameters:
            parameters = cls._add_task_classes(parameters)

        return parameters

    def _load_variables(self, dag, parameters):
        with AWSClient("dynamodb") as dynamodb:
            for task, task_variables in parameters.items():
                self._load_variables_into_dynamodb(dynamodb, dag, task, task_variables)

    @classmethod
    def _get_dag_id(cls, var_tree):
        global_variables = var_tree.get_branch_values([])
        dag = None

        for key, value in global_variables.items():
            if value is None:
                dag = key
                break

        return dag

    @classmethod
    def _get_global_variables(cls, dag, var_tree):
        global_variables = var_tree.get_branch_values([])

        global_variables.pop(dag)

        return global_variables

    @classmethod
    def _expand_task_parameters(cls, parameters):
        deleted_tasks = []
        expanded_task_parameters = []

        for task, task_parameters in parameters.items():
            if '@MACRO_COUNT@' in task_parameters:
                deleted_tasks.append(task)

                expanded_task_parameters += cls._generate_macro_parameters(task, task_parameters)

        for task in deleted_tasks:
            parameters.pop(task)

        for task_parameters in expanded_task_parameters:
            parameters.update(task_parameters)

        return parameters

    @classmethod
    def _add_task_classes(cls, parameters):
        dag_class = import_plugin(parameters["DAG"]["DAG_CLASS"])

        for task, task_parameters in parameters.items():
            if task not in ("GLOBAL", "DAG", "LOCAL") and "TASK_CLASS" not in task_parameters:
                parameters[task] = cls._add_task_class(dag_class, task, task_parameters)

        for task in dag_class.tasks:
            if task not in parameters:
                parameters[task] = cls._add_task_class(dag_class, task, {})

        return parameters

    def _load_variables_into_dynamodb(self, dynamodb, dag, task, variables):
        response = None
        item = self._generate_item(dag, task, variables)

        response = dynamodb.put_item(TableName=self._table, Item=item)

        return response

    @classmethod
    def _generate_macro_parameters(cls, task, task_parameters):
        count = int(task_parameters['@MACRO_COUNT@'])
        generated_parameters = []


        for index in range(count):
            instance_parameters = {
                name: cls._replace_macro_parameters(value, count, index) for name, value in task_parameters.items()
                if name != '@MACRO_COUNT@'
            }

            generated_parameters.append({f'{task}_{index}': instance_parameters})

        return generated_parameters

    @classmethod
    def _add_task_class(cls, dag_class, task, task_parameters):
        task_class = dag_class.task_class(task)
        task_class_name = task_class

        if hasattr(task_class, "name"):
            task_class_name = task_class.name

        task_parameters["TASK_CLASS"] = task_class_name

        return task_parameters

    @classmethod
    def _generate_item(cls, dag, task, variables):
        item = dict(
            Task=dict(S=task),
            DAG=dict(S=dag),
            Variables=dict(S=json.dumps(variables))
        )

        return item

    @classmethod
    def _replace_macro_parameters(cls, value, macro_count, macro_index):
        resolved_value = value

        if hasattr(value, 'replace'):
            resolved_value = value.replace('@MACRO_COUNT@', str(macro_count))
            resolved_value = resolved_value.replace('@MACRO_INDEX@', str(macro_index))

        return resolved_value

class IncompleteConfigurationException(Exception):
    pass

class Configuration:
    def __init__(self, table: str):
        self._table = table

    def get_dags(self) -> list:
        dags = set()
        with AWSClient("dynamodb") as dynamodb:
            response = dynamodb.scan(TableName=self._table)

        for item in response["Items"]:
            dags.add(item["DAG"]["S"])

        return dags

    def get_tasks(self, dag: str):
        tasks = []

        parameters = dict(
            TableName=self._table,
            FilterExpression="DAG = :dag",
            ExpressionAttributeValues={":dag": {"S": dag}}
        )

        with AWSClient("dynamodb") as dynamodb:
            response = dynamodb.scan(**parameters)

        for item in response["Items"]:
            task = item["Task"]["S"]

            if task not in ["DAG", "GLOBAL", "LOCAL"]:
                tasks.append(task)

        return tasks

    def clear_dag(self, dag: str):
        parameters = dict(
            TableName=self._table,
            FilterExpression="DAG = :dag",
            ExpressionAttributeValues={":dag": {"S": dag}}
        )

        with AWSClient("dynamodb") as dynamodb:
            response = dynamodb.scan(**parameters)

            for item in response["Items"]:
                dynamodb.delete_item(
                    TableName=self._table,
                    Key={'DAG': {'S': dag}, 'Task': {'S': item["Task"]["S"]}},
                )
