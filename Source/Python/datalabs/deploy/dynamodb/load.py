""" Tool for loading Kubernetes ConfigMap data into etcd. """
import base64
import logging

import yaml
from   boto3.dynamodb.conditions import Key, And


from   datalabs.access.aws import AWSClient
from   datalabs.access.environment import VariableTree

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class ConfigMapLoader():
    def __init__(self, config):
        self._config = config

    def load(self, filename):
        variables = self._extract_variables_from_configmap(filename)

        dag_variables = self._parse_variables(variables)

        for task, task_variables in dag_variables.items():
            self._load_variables_into_dynamodb(task, task_variables)

    @classmethod
    def _extract_variables_from_configmap(cls, filename):
        with open(filename) as file:
            configmap = yaml.safe_load(file.read())

        return configmap['data']

    def _parse_variables(self, variables):
        dag_variables = dict()
        var_tree = VariableTree.generate(variables)
        global_variables = var_tree.get_branches([])
        tasks = var_tree.get_branches([self._config["dag"]])

        global_variables.remove(self._config["dag"])

        for task in tasks:
            dag_variables[task] = var_tree.get_branch_values([self._config["dag"], task])

        return dag_variables


    def _load_variables_into_dynamodb(self, task, variables):
        response = None
        item = self._generate_item(task, variables)

        with AWSClient("dynamodb") as dynamodb:
            import pdb; pdb.set_trace()
            # TODO: delete all items for DAG
            # dynamodb.query(TableName='DataLake-configuration-sbx', KeyConditions=dict(DAG=dict(ComparisonOperator="EQ", AttributeValueList=[dict(S="ONEVIEW")])))
            response = dynamodb.put_item(TableName=self._config["table"], Item=item)

        return response

    def _generate_item(self, task, variables):
        item = dict(
            Task=dict(S=task),
            DAG=dict(S=self._config["dag"])
        )

        for key, value in variables.items():
            item[key] = dict(S=str(value))

        # TODO: add in global variables

        return item
