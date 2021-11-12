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

        parameters = self._expand_macros(parameters)

        with AWSClient("dynamodb") as dynamodb:
            for task, task_variables in parameters.items():
                self._load_variables_into_dynamodb(dynamodb, dag, task, task_variables)

    @classmethod
    def _extract_variables_from_config(cls, filenames):
        config = dict()

        for filename in filenames:
            with open(filename) as file:
                config.update(yaml.safe_load(file.read())['data'])

        for key, value in config.items():
            if not isinstance(value, str):
                raise ValueError(f'The value for parameter {key} is not a string, but is {type(value)}: {value}.')

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

    @classmethod
    def _expand_macros(cls, parameters):
        deleted_tasks = []
        added_tasks = []

        for task, task_parameters in parameters.items():
            if '@MACRO_COUNT@' in task_parameters:
                deleted_tasks.append(task)

                added_tasks += cls._generate_macro_parameters(task, task_parameters)

        for task in deleted_tasks:
            parameters.pop(task)

        for task_parameters in added_tasks:
            parameters.update(task_parameters)

        return parameters

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
    def _replace_macro_parameters(cls, value, macro_count, macro_index):
        resolved_value = value

        if hasattr(value, 'replace'):
            resolved_value = value.replace('@MACRO_COUNT@', str(macro_count))
            resolved_value = resolved_value.replace('@MACRO_INDEX@', str(macro_index))

        return resolved_value

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
