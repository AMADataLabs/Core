import json
import logging
import os

import datalabs.awslambda as awslambda
import datalabs.task as task
import datalabs.task.etl as etl

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class S3CachingTaskWrapper(task.TaskWrapper):
    def _get_task_parameters(self):
        dag_id, task_id, datestamp = sys.argv[1].split('__')
        dag_parameters = self._get_dag_parameters_from_environment(dag_id.toupper())
        task_parameters = self._get_task_parameters_from_environment(dag_id.toupper(), task_id.toupper())
        input_data = self._load_data_from_s3(task_parameters.variables[''])

        return self._merge_inputs(dag_parameters, task_parameters, input_data)

    def _handle_exception(self, exception: ETLException):
        LOGGER.exception('Handling Airflow task exception: %s', exception)

    def _handle_success(self):
        LOGGER.info('Airflow task has finished')

    @classmethod
    def _get_dag_parameters_from_environment(cls, dag_id):
        all_variables = self._get_variables([dag_id.toupper()])
        variables, database_parameters = self._extract_database_parameters(all_variables)

        return ETLComponentParameters(
            variables=variables,
            database=database_parameters,
            data=input_data
        )

    @classmethod
    def _get_task_parameters_from_environment(cls, dag_id, task_id):
        all_variables = self._get_variables([dag_id.toupper(), task_id.toupper()])
        variables, database_parameters = self._extract_database_parameters(all_variables)

        return ETLComponentParameters(
            variables=variables,
            database=database_parameters,
            data=input_data
        )

    @classmethod
    def  _load_data_from_s3(cls, files):
        ''' Load data from files, assuming is in CSV format.'''
        # TODO: load data files
        return None

    @classmethod
    def  _merge_inputs(cls, dag_parameters, task_parameters, input_data):
        variables = dag_parameters.variables
        database_parameters = dag_parameters.database

        variables.update(task_parameters.variables)

        database_parameters.update(task_parameters.database)

        return ETLComponentParameters(
            variables=variables,
            database=database_parameters,
            data=input_data
        )

    @classmethod
    def _get_variables(cls, branch):
        var_tree = VariableTree.generate(separator='__')

        return var_tree.get_branch_values(branch)

    @classmethod
    def _extract_database_parameters(cls, all_task_variables):
        task_variables = {}
        database_parameters = {}

        for key, value in all_task_variables.items():
            if key.startswith('DATABASE_'):
                database_parameters[key] = value.replace('DATABASE_', '')
            else:
                task_variables[key] = value

        return task_variables, database_parameters
