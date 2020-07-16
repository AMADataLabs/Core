""" REPLACE WITH DOCSTRING """
import logging
import os

from   datalabs.etl.task import ETLParameters, ETLException
from   datalabs.awslambda import TaskWrapper

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class ETLTaskWrapper(TaskWrapper):
    def _get_task_parameters(self, event: dict):
        return ETLParameters(
            extractor=self._generate_parameters(os.environ, "EXTRACTOR"),
            transformer=self._generate_parameters(os.environ, "TRANSFORMER"),
            loader=self._generate_parameters(os.environ, "LOADER"),
        )

    def _handle_exception(self, exception: ETLException) -> (int, dict):
        LOGGER.error('Handling ETL task exception: %s', exception)
        status_code = 400
        body = dict(message=str(exception))

        return status_code, body

    def _generate_response(self, task) -> (int, dict):
        return 200, dict()

    @classmethod
    def _generate_parameters(cls, variables, variable_base_name):
        LOGGER.debug('Variables: %s', variables)
        LOGGER.debug('Variable Base Name: %s', variable_base_name)
        parameters = {
            name[len(variable_base_name)+1:]:value
            for name, value in variables.items()
            if name.startswith(variable_base_name + '_')
        }

        if not parameters:
            LOGGER.debug('parameters: %s', parameters)
            LOGGER.warning('No parameters for "%s" in %s', variable_base_name, variables)

        return parameters
