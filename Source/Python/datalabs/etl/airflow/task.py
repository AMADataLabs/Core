from   abc import ABC, abstractmethod
import json
import logging
import os

from   datalabs.access.environment import VariableTree
import datalabs.awslambda as awslambda
import datalabs.etl.task as etl
from   datalabs.plugin import import_plugin
import datalabs.task as task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class AirflowTaskWrapper(task.TaskWrapper):
    def _get_task_parameters(self):
        parameters = self._get_dag_task_parameters()
        cache_plugin = self._get_cache_plugin(parameters.variables)
        input_data = cache_plugin.extract_data()

        parameters.data = input_data

        return parameters

    def _handle_exception(self, exception: etl.ETLException):
        LOGGER.exception('Handling Airflow task exception: %s', exception)

    def _handle_success(self):
        cache_plugin = self._get_cache_plugin(parameters.variables)
        cache_plugin.load_data(self._task.data)

        LOGGER.info('Airflow task has finished')

    def _get_dag_task_parameters(self):
        args = self._parameters
        dag_id, task_id, datestamp = args[1].split('__')
        dag_parameters = self._get_dag_parameters_from_environment(dag_id.upper())
        task_parameters = self._get_task_parameters_from_environment(dag_id.upper(), task_id.upper())

        return self._merge_parameters(dag_parameters, task_parameters)

    @classmethod
    def _get_cache_plugin(cls, task_variables):
        cache_variables = cls._get_cache_variables(task_variables)
        plugin_name = 'datalabs.etl.airflow.s3.S3TaskDataCache'

        if 'CLASS' in cache_variables:
            plugin_name = cache_variables['CLASS']

        Plugin = import_plugin(plugin_name)

        return Plugin(cache_variables)

    @classmethod
    def _get_dag_parameters_from_environment(cls, dag_id):
        variables = cls._get_variables([dag_id.upper()])

        return etl.ETLComponentParameters(variables=variables)

    @classmethod
    def _get_task_parameters_from_environment(cls, dag_id, task_id):
        variables = cls._get_variables([dag_id.upper(), task_id.upper()])

        return etl.ETLComponentParameters(variables=variables)

    @classmethod
    def  _merge_parameters(cls, dag_parameters, task_parameters):
        variables = dag_parameters.variables

        variables.update(task_parameters.variables)

        return etl.ETLComponentParameters(variables=variables)

    @classmethod
    def _get_cache_variables(cls, task_variables):
        cache_variables = {}

        for key, value in task_variables.items():
            if key.startswith('CACHE_'):
                cache_variables[key.replace('CACHE_', '')] = value

        return cache_variables

    @classmethod
    def _get_variables(cls, branch):
        var_tree = VariableTree.generate()

        return var_tree.get_branch_values(branch)


class TaskDataCache:
    def __init__(self, cache_variables):
        self._variables = cache_variables

    @abstractmethod
    def extract_data(self):
        return None

    @abstractmethod
    def load_data(self, output_data):
        pass
