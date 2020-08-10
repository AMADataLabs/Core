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
        return 200, dict(), dict()

    def _handle_exception(self, exception: task.ETLException) -> (int, dict):
        LOGGER.error('Handling ETL task exception: %s', exception)

        return 400, dict(), dict(message=str(exception))
