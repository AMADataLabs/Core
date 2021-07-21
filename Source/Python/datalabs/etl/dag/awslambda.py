""" Task wrapper for DAG and DAG task Lambda functions. """
import json
import logging
import os

from   datalabs.access.parameter.dynamodb import DynamoDBEnvironmentLoader
from   datalabs.etl.task import ExecutionTimeMixin
import datalabs.etl.dag.task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class DynamoDBTaskParameterGetterMixin:
    # pylint: disable=redefined-outer-name
    @classmethod
    def _get_dag_task_parameters_from_dynamodb(cls, dag: str, task: str):
        parameters = {}

        dynamodb_loader = DynamoDBEnvironmentLoader(dict(
            table=os.environ["DYNAMODB_CONFIG_TABLE"],
            dag=dag,
            task=task
        ))
        dynamodb_loader.load(environment=parameters)

        return parameters


class ProcessorTaskWrapper(ExecutionTimeMixin, DynamoDBTaskParameterGetterMixin, datalabs.etl.dag.task.DAGTaskWrapper):
    def _get_runtime_parameters(self, parameters):
        LOGGER.debug('Event: %s', parameters)
        event_parameters = None

        if not hasattr(parameters, "items"):
            raise ValueError(f'Invalid Lambda event: {parameters}')

        event_parameters = self._get_sns_event_parameters(parameters)

        if len(event_parameters) == 1 and 'Records' in event_parameters:
            event_parameters = self._get_s3_event_parameters(event_parameters)

        if "task" not in event_parameters:
            event_parameters["task"] = "DAG"

        return event_parameters

    @classmethod
    def _get_sns_event_parameters(cls, event):
        ''' An SNS notification implies either the DAG Processor or the Task Processor,
             so just return the deserialized event message as the parameters.
        '''
        record = event.get("Records", [{}])[0]
        event_source = record.get("EventSource", record.get("eventSource"))

        if event_source != 'aws:sns':
            raise ValueError(f'Invalid SNS event: {event}')

        return json.loads(record["Sns"]["Message"])


    def _get_s3_event_parameters(self, event):
        ''' An S3 notification implies that the DAG Scheduler should be run, so return appropriate
            parameters for the DAG Processor assuming the DAG Scheduler as the DAG to execute.
        '''
        record = event.get("Records", [{}])[0]
        event_source = record.get("EventSource", record.get("eventSource"))
        dag = "DAG_SCHEDULER"

        if event_source != 'aws:s3':
            raise ValueError(f'Invalid S3 notification event: {event}')

        return dict(
            dag=dag,
            execution_time=self.execution_time.isoformat()
        )

    def _handle_success(self) -> (int, dict):
        return "Success"

    def _handle_exception(self, exception) -> (int, dict):
        LOGGER.error('Handling DAG task exception: %s', exception)

        return f'Failed: {str(exception)}'

    def _get_dag_task_parameters(self):
        ''' Get parameters for either the DAG Processor or the Task Processor. '''
        dag = self._get_dag_id()
        task = self._get_task_id()
        dag_task_parameters = dict(
            dag=dag,
            execution_time=self._get_execution_time(),
        )

        dag_task_parameters.update(self._get_dag_task_parameters_from_dynamodb(dag, "DAG"))

        if task != "DAG":
            dag_task_parameters["task"] = task

        return dag_task_parameters


class DAGTaskWrapper(DynamoDBTaskParameterGetterMixin, datalabs.etl.dag.task.DAGTaskWrapper):
    @classmethod
    def _get_runtime_parameters(cls, parameters):
        LOGGER.info('Event Parameters: %s', parameters)

        return parameters

    def _handle_success(self) -> (int, dict):
        return "Success"

    def _handle_exception(self, exception) -> (int, dict):
        LOGGER.error('Handling DAG task exception: %s', exception)

        return f'Failed: {str(exception)}'

    def _get_dag_task_parameters(self):
        dag = self._get_dag_id()
        task = self._get_task_id()
        dag_task_parameters = self._get_dag_task_parameters_from_dynamodb(dag, task)

        if task == 'DAG':
            dag_parameters = self._get_dag_task_parameters_from_dynamodb(self._get_dag_id(), "DAG")
            dag_task_parameters["dag"] = dag
            dag_task_parameters["dag_class"] = dag_parameters["DAG_CLASS"]

        return dag_task_parameters
