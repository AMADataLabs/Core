""" Tool for loading Kubernetes ConfigMap data into DynamoDB. """
import json
import logging

import yaml

from   datalabs.access.aws import AWSClient
from   datalabs.access.environment import VariableTree

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class ConfigMapLoader():
    def __init__(self, parameters):
        self._parameters = parameters

    def load(self, filenames):
        variables = self._extract_variables_from_config(filenames)

        dag, parameters = self._parse_variables(variables)

        with AWSClient("dynamodb") as dynamodb:
            for task, task_variables in parameters.items():
                self._load_variables_into_dynamodb(dynamodb, dag, task, task_variables)

    @classmethod
    def _extract_variables_from_config(cls, filenames):
        config = dict()

        for filename in filenames:
            with open(filename) as file:
                config.update(yaml.safe_load(file.read())['data'])

        return config

    def _parse_variables(self, variables):
        parameters = dict()
        var_tree = VariableTree.generate(variables)
        dag = self._get_dag_id(var_tree)
        parameters["GLOBAL"] = self._get_global_variables(dag, var_tree)
        tasks = var_tree.get_branches([dag])

        for task in tasks:
            parameters[task] = var_tree.get_branch_values([dag, task])

        return (dag, parameters)

    def _load_variables_into_dynamodb(self, dynamodb, dag, task, variables):
        response = None
        item = self._generate_item(dag, task, variables)

        response = dynamodb.put_item(TableName=self._parameters["table"], Item=item)

        return response

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
    def _generate_item(cls, dag, task, variables):
        item = dict(
            Task=dict(S=task),
            DAG=dict(S=dag),
            Variables=dict(S=json.dumps(variables))
        )

        return item
