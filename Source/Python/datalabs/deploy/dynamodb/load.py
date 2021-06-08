""" Tool for loading Kubernetes ConfigMap data into etcd. """
import base64
import logging

import yaml

from   datalabs.access.aws import AWSClient
from   datalabs.access.environment import VariableTree

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class ConfigMapLoader():
    def __init__(self, etcd_config):
        self._etcd_config = etcd_config

    def load(self, filename):
        variables = self._extract_variables_from_configmap(filename)

        dag, task_variables = self._deconstruct_task_variables(variables)

        self._load_variables_into_dynamodb(variables)

    @classmethod
    def _extract_variables_from_configmap(cls, filename):
        with open(filename) as file:
            configmap = yaml.safe_load(file.read())

        return list(configmap['data'].items())

    @classmethod
    def _deconstruct_task_variables(cls, variables):
        dag = None
        task_variables = dict()
        var_tree = VariableTree.generate(variables)
        var_tree.get_branch_values([component]) or {}


    def _load_variables_into_dynamodb(self, variables):
        with AWSClient("dynamodb") as dynamodb:
            table = dynamodb.Table(self._parameters.state_lock_table)

            responses.append(etcd.execute_transaction(transaction))

        return responses
