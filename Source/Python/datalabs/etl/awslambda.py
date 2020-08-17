""" REPLACE WITH DOCSTRING """
import logging
import os

import datalabs.awslambda as awslambda
import datalabs.etl.task as task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class ETLTaskWrapper(task.ETLTaskParametersGetterMixin, awslambda.TaskWrapper):
    def _generate_response(self) -> (int, dict):
        return "Success"

    def _handle_exception(self, exception: task.ETLException) -> (int, dict):
        LOGGER.error('Handling ETL task exception: %s', exception)

        return f'Failed: {str(exception)}'
