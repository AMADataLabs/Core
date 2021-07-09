""" Task wrapper for DAG and DAG task Lambda functions. """
import json
import logging
import os

from   datalabs.access.parameter.dynamodb import DynamoDBEnvironmentLoader
import datalabs.etl.dag.task as task
from   datalabs.plugin import import_plugin

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class DAGTaskWrapper(task.DAGTaskWrapper):
    def _handle_success(self) -> (int, dict):
        return "Success"

    def _handle_exception(self, exception) -> (int, dict):
        LOGGER.error('Handling ETL task exception: %s', exception)

        return f'Failed: {str(exception)}'

    def _get_dag_parameters(self):
        dag_parameters = super()._get_dag_parameters()

        dag_parameters["DAG_CLASS"] = import_plugin(os.environ["DAG_CLASS"])
        dag_parameters["STATE_CLASS"] = import_plugin(os.environ["STATE_CLASS"])

        return dag_parameters

    def _get_dag_task_parameters(self):
        dag_task_parameters = super()._get_dag_task_parameters()

        dag_task_parameters.update(self._get_event_parameters(self._parameters))

        if self._parameters["type"] == 'Task':
            dynamodb_loader = DynamoDBEnvironmentLoader(dict(
                table=os.environ["DYNAMODB_CONFIG_TABLE"],
                dag=self._get_dag_id(),
                task=self._get_task_id()
            ))
            dynamodb_loader.load(environment=dag_task_parameters)

        return dag_task_parameters

    def _get_dag_id(self):
        return self._parameters["dag"]

    def _get_task_id(self):
        return self._parameters["task"]

    def _get_event_parameters(self, event):
        LOGGER.info('Event Parameters: %s', event)

        return event


class ProcessorWrapper(DAGTaskWrapper):
    @classmethod
    def _get_event_parameters(cls, event):
        LOGGER.debug('Event: %s', event)
        event_parameters = {}

        if not hasattr(event, "items") or 'Records' not in event:
            raise ValueError(f'Invalid SNS event: {event}')

        for record in event["Records"]:
            if record.get("EventSource") == 'aws:sns':
                event_parameters = json.loads(record["Message"])

                break

        if len(event_parameters) == 1 and 'Records' in event_parameters:
            event_parameters = {}

        return event_parameters

    def _get_task_id(self):
        return ""
