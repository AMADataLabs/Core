import os

from   datalabs.etl.task import ETLTask, ETLParameters, ETLException
from   datalabs.awslambda import TaskWrapper


class ETLTaskWrapper(TaskWrapper):
    def _get_task_parameters(self, event: dict):
        return ETLParameters(
            extractor=self._generate_parameters(os.environ, "EXTRACTOR"),
            transformer=self._generate_parameters(os.environ, "TRANSFORMER"),
            loader=self._generate_parameters(os.environ, "LOADER"),
            database=dict(
                name=os.getenv('DATABASE_NAME'),
                backend=os.getenv('DATABASE_BACKEND'),
                host=os.getenv('DATABASE_HOST'),
                username=os.getenv('DATABASE_USERNAME'),
                password=os.getenv('DATABASE_PASSWORD')
            ),
        )

    def _handle_exception(self, exception: APIEndpointException) -> (int, dict):
        status_code = exception.status_code
        body = dict(message=exception.message)

        return status_code, body

    def _generate_response(self, task) -> (int, dict):
        return task.status_code, task.response_body

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
            LOGGER.warn(f'No parameters for "{variable_base_name}" in {variables}')

        return parameters
