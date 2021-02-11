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
        dag_parameters = self._get_dag_parameters_from_environment(dag_id.upper())
        task_parameters = self._get_task_parameters_from_environment(dag_id.upper(), task_id.upper())
        input_data = self._extract_data_from_s3(task_parameters.variables)

        return self._merge_inputs(dag_parameters, task_parameters, input_data)

    def _handle_exception(self, exception: ETLException):
        LOGGER.exception('Handling Airflow task exception: %s', exception)

    def _handle_success(self):
        self._load_data_to_s3(self._task.data, self._task.parameters.variables)

        LOGGER.info('Airflow task has finished')

    @classmethod
    def _get_dag_parameters_from_environment(cls, dag_id):
        all_variables = self._get_variables([dag_id.upper()])
        variables, database_parameters = self._extract_database_parameters(all_variables)

        return ETLComponentParameters(
            variables=variables,
            database=database_parameters,
            data=input_data
        )

    @classmethod
    def _get_task_parameters_from_environment(cls, dag_id, task_id):
        all_variables = self._get_variables([dag_id.upper(), task_id.upper()])
        variables, database_parameters = self._extract_database_parameters(all_variables)

        return ETLComponentParameters(
            variables=variables,
            database=database_parameters,
            data=input_data
        )

    @classmethod
    def  _extract_data_from_s3(cls, task_variables):
        ''' Pull cached data from files on S3, assuming is in CSV format.'''
        cache_variables = cls._get_cache_variables(task_variables)
        cache_parameters = ETLComponentParameters(variables=cache_variables)
        cache_extractor = S3FileExtractorTask(cache_parameters)

        cache_extractor.run()

        return cache_extractor.data

    @classmethod
    def  _load_data_to_s3(cls, task_output_data, task_variables):
        cache_variables = cls._get_cache_variables(task_variables)
        cache_parameters = ETLComponentParameters(variables=cache_variables)
        cache_loader = S3FileLoaderTask(cache_parameters)

        cache_loader.run()

        return cache_loader.data

    @classmethod
    def  _merge_inputs(cls, dag_parameters, task_parameters, input_data):
        variables = dag_parameters.variables

        variables.update(task_parameters.variables)

        return ETLComponentParameters(
            variables=variables,
            data=input_data
        )

    @classmethod
    def _get_variables(cls, branch):
        var_tree = VariableTree.generate()

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

    @classmethod
    def _get_cache_variables(cls, task_variables):
        cache_variables = {}

        for key, value in task_variables.items():
            if key.startswith('CACHE_'):
                cache_variables[key.replace('CACHE_', '')] = value

        return cache_variables
