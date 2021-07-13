""" Task wrapper for DAG and DAG task Lambda functions. """
import json
import logging
import os

from   datalabs.access.parameter.dynamodb import DynamoDBEnvironmentLoader
from   datalabs.etl.task import ExecutionTimeMixin
import datalabs.etl.dag.task as task
from   datalabs.plugin import import_plugin

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class DAGTaskWrapper(task.DAGTaskWrapper):
    @classmethod
    def _get_runtime_parameters(cls, parameters):
        LOGGER.info('Event Parameters: %s', parameters)

        return parameters

    def _handle_success(self) -> (int, dict):
        return "Success"

    def _handle_exception(self, exception) -> (int, dict):
        LOGGER.error('Handling ETL task exception: %s', exception)

        return f'Failed: {str(exception)}'

    def _get_dag_parameters(self):
        dag_parameters = super()._get_dag_parameters()

        dynamodb_loader = DynamoDBEnvironmentLoader(dict(
            table=os.environ["DYNAMODB_CONFIG_TABLE"],
            dag=self._get_dag_id(),
            task="GLOBAL"
        ))
        dynamodb_loader.load(environment=dag_parameters)

        dag_parameters["DAG_CLASS"] = import_plugin(os.environ["DAG_CLASS"])
        dag_parameters["STATE_CLASS"] = import_plugin(os.environ["STATE_CLASS"])

        return dag_parameters

    def _get_dag_task_parameters(self):
        dag_task_parameters = super()._get_dag_task_parameters()

        dag_task_parameters.update(self._parameters)

        if self._parameters["type"] == 'Task':
            dynamodb_loader = DynamoDBEnvironmentLoader(dict(
                table=os.environ["DYNAMODB_CONFIG_TABLE"],
                dag=self._get_dag_id(),
                task=self._get_task_id()
            ))
            dynamodb_loader.load(environment=dag_task_parameters)

        return dag_task_parameters

    def _get_dag_id(self):
        return self._runtime_parameters["dag"]

    def _get_task_id(self):
        return self._runtime_parameters.get("task")


class ProcessorTaskWrapper(ExecutionTimeMixin, DAGTaskWrapper):
    def _get_runtime_parameters(self, parameters):
        LOGGER.debug('Event: %s', parameters)
        event_parameters = {}

        if not hasattr(parameters, "items") or 'Records' not in parameters:
            raise ValueError(f'Invalid SNS event: {parameters}')

        for record in parameters["Records"]:
            event_source = record.get("EventSource", record.get("eventSource"))
            if event_source == 'aws:sns':
                sns_details = record["Sns"]
                event_parameters = json.loads(sns_details["Message"])
            elif event_source == 'aws:s3':
                event_parameters = dict(dag="DAG_SCHEDULER", execution_time=self.execution_time.isoformat())

        if len(event_parameters) == 1 and 'Records' in event_parameters:
            event_parameters = self._get_runtime_parameters(event_parameters)

        return event_parameters

    def _get_task_id(self):
        return ""
