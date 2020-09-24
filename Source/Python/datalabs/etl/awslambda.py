""" REPLACE WITH DOCSTRING """
import logging

import datalabs.awslambda as awslambda
import datalabs.etl.task as task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class ETLTaskWrapper(task.ETLTaskParametersGetterMixin, awslambda.TaskWrapper):
    def _get_task_parameters(self):
        task_parameters = super()._get_task_parameters()

        if self._parameters and hasattr(self._parameters, 'items'):
            task_parameters = self._add_component_environment_variables_from_event(task_parameters, self._parameters)

        return task_parameters

    def _generate_response(self) -> (int, dict):
        return "Success"

    def _handle_exception(self, exception: task.ETLException) -> (int, dict):
        LOGGER.error('Handling ETL task exception: %s', exception)

        return f'Failed: {str(exception)}'

    @classmethod
    def _add_component_environment_variables_from_event(cls, task_parameters, event):
        environment_variables = {key.upper():str(value) for key, value in event.items()}
        component_variables = [
            task_parameters.extractor.variables,
            task_parameters.transformer.variables,
            task_parameters.loader.variables
        ]

        for variables in component_variables:
            variables.update(environment_variables)

        return task_parameters
