""" REPLACE WITH DOCSTRING """
import logging
import os

from   datalabs.etl.task import ETLParameters, ETLException, ETLComponentParameters
from   datalabs.awslambda import TaskWrapper

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class ETLTaskWrapper(TaskWrapper):
    def _get_task_parameters(self, event: dict):
        return ETLParameters(
            extractor=self._get_component_parameters(self._generate_parameters(os.environ, "EXTRACTOR")),
            transformer=self._get_component_parameters(self._generate_parameters(os.environ, "TRANSFORMER")),
            loader=self._get_component_parameters(self._generate_parameters(os.environ, "LOADER"))
        )

    def _handle_exception(self, exception: ETLException) -> (int, dict):
        LOGGER.error('Handling ETL task exception: %s', exception)

        return 400, dict(), dict(message=str(exception))

    def _generate_response(self, task) -> (int, dict):
        return 200, dict(), dict()

    @classmethod
    def _generate_parameters(cls, variables, variable_base_name):
        LOGGER.debug('Variables: %s', variables)
        LOGGER.debug('Variable Base Name: %s', variable_base_name)
        parameters = {
            name[len(variable_base_name)+1:]:value
            for name, value in variables.items()
            if name.startswith(variable_base_name + '_')
        }
        LOGGER.debug('Parameters: %s', parameters)

        if not parameters:
            LOGGER.debug('parameters: %s', parameters)

        return parameters

    @classmethod
    def _get_component_parameters(cls, variables):
        database_variables = cls._generate_parameters(variables, 'DATABASE')
        database_parameters = {key.lower(): value for key, value in database_variables.items()}
        LOGGER.debug('Database variables: %s', database_variables)
        component_variables = {key: value for key, value in variables.items() if not key.startswith('DATABASE_')}
        LOGGER.debug('Component variables: %s', component_variables)

        return ETLComponentParameters(database=database_parameters, variables=component_variables)
