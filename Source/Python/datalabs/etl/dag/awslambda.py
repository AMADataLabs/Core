""" Task wrapper for DAG and DAG task Lambda functions. """
import logging
import os

from   datalabs.access.parameter.dynamodb import DynamoDBEnvironmentLoader
import datalabs.awslambda as awslambda
import datalabs.etl.task as task
from   datalabs.plugin import import_plugin

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class DAGTaskWrapper(awslambda.TaskWrapper):
    def __init__(self, parameters=None):
        super().__init__(parameters)

        self._cache_parameters = {}

    def _setup_environment(self):
        """ Add extra fields to the TaskWrapper parameters for the TaskResolver. We expect that the
            following fields are included in the event details that are used as TaskWrapper parameters:
            {
                "type": "string",
                "execution_time": "string",
                "task": "string" (only if type is "DAG")
            }
         """
        super()._setup_environment()

        self._parameters["dag_class"] = import_plugin(os.environ["DAG_CLASS"])

    def _get_task_parameters(self):
        task_parameters = None

        dag_parameters = self._get_dag_parameters()

        if self._parameters["type"] == 'Task':
            task_parameters = self._get_dag_task_parameters()

            task_parameters.update(dag_parameters)

        return task_parameters

    def _handle_success(self) -> (int, dict):
        return "Success"

    def _handle_exception(self, exception: task.ETLException) -> (int, dict):
        LOGGER.error('Handling ETL task exception: %s', exception)

        return f'Failed: {str(exception)}'

    def _get_dag_parameters(self):
        return dict(
            dag_class=self._parameters["dag_class"],
            dag_state_class=import_plugin(os.environ["DAG_STATE_CLASS"])
        )

    def _get_dag_task_parameters(self):
        dag_task_parameters = {}

        dynamodb_loader = DynamoDBEnvironmentLoader(dict(
            table=os.environ["DYNAMODB_CONFIG_TABLE"],
            dag=os.environ["DAG"],
            task=self._parameters["task"]
        ))
        dynamodb_loader.load(environment=dag_task_parameters)

        return dag_task_parameters
