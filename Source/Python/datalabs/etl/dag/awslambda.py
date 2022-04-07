""" Task wrapper for DAG and DAG task Lambda functions. """
import json
import logging
import urllib.parse
from   dateutil.parser import isoparse

from   datalabs.etl.task import ExecutionTimeMixin
import datalabs.etl.dag.aws as aws
import datalabs.etl.dag.task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class ProcessorTaskWrapper(
    ExecutionTimeMixin,
    aws.DynamoDBTaskParameterGetterMixin,
    datalabs.etl.dag.task.DAGTaskWrapper
):
    def _get_runtime_parameters(self, parameters):
        LOGGER.debug('Event: %s', parameters)
        event_parameters = None

        if not hasattr(parameters, "items"):
            raise ValueError(f'Invalid Lambda event: {parameters}')

        event_parameters = self._get_sns_event_parameters(parameters)
        LOGGER.debug('SNS Event Parameters: %s', event_parameters)

        if len(event_parameters) == 1 and 'Records' in event_parameters:
            LOGGER.info('Processing S3 Event Trigger...')
            event_parameters = self._get_s3_event_parameters(event_parameters)
        elif "source" in event_parameters:
            LOGGER.info('Processing CloudWatch Event Trigger...')
            event_parameters = self._get_cloudwatch_event_parameters(event_parameters)

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
        ''' An S3 notification implies that the DAG Scheduler should be run.'''
        record = event.get("Records", [{}])[0]
        event_source = record.get("EventSource", record.get("eventSource"))
        parameters = None

        if event_source != 'aws:s3':
            raise ValueError(f'Invalid S3 notification event: {event}')

        s3_object_key = record["s3"]["object"]["key"]
        LOGGER.debug('S3 Event Object: %s', s3_object_key)

        if s3_object_key == "schedule.csv":
            LOGGER.info('Processing schedule file update trigger...')
            parameters = self._get_scheduler_event_parameters()
        elif not '__' in s3_object_key:
            raise ValueError(
                f'Invalid S3 object name: {s3_object_key}. The name must either be equal to "schedule.csv" '
                f'or conform to the format "<DAG_ID>__<ISO-8601_EXECUTION_TIME>" format.')
        else:
            LOGGER.info('Processing backfill file trigger...')
            parameters = self._get_backfill_parameters(s3_object_key)

        return parameters

    def _get_cloudwatch_event_parameters(self, event):
        ''' A CloudWatch Event notification implies that the DAG Scheduler should be run.'''
        event_source = event["source"]

        if event_source != 'aws.events':
            raise ValueError(f'Invalid CloudWatch event: {event}')

        return self._get_scheduler_event_parameters()

    def _get_scheduler_event_parameters(self):
        ''' Return appropriate parameters for the DAG Processor assuming the DAG Scheduler as the DAG to execute.'''
        return dict(
            dag="DAG_SCHEDULER",
            execution_time=self.execution_time.isoformat()
        )

    @classmethod
    def _get_backfill_parameters(cls, s3_object_key):
        dag_id, escaped_execution_time = s3_object_key.rsplit("__", 1)
        execution_time = urllib.parse.unquote(escaped_execution_time).replace('T', ' ')

        try:
            isoparse(execution_time)  # Check if execution_time is ISO-8601
        except ValueError as error:
            raise ValueError(
                f'Backfill execution time is not a valid ISO-8601 timestamp: {execution_time}. ' \
                f'The backfill S3 object name must conform to the format "<DAG_ID>__<ISO-8601_EXECUTION_TIME>".'
            ) from error


        return dict(
            dag=dag_id,
            execution_time=execution_time
        )

    def _handle_success(self) -> (int, dict):
        return "Success"

    def _handle_exception(self, exception) -> (int, dict):
        LOGGER.exception(
            'An exception occured while attempting to send a run notification for task %s of DAG %s.',
            self._get_task_id(),
            self._get_dag_id()
        )

        return f'Failed: {str(exception)}'

    def _get_dag_task_parameters(self):
        ''' Get parameters for either the DAG Processor or the Task Processor. '''
        dag = self._get_dag_id()
        task = self._get_task_id()
        dag_parameters = dict(
            dag=dag,
            execution_time=self._get_execution_time(),
        )
        dag_parameters.update(self._get_dag_task_parameters_from_dynamodb(dag, "DAG"))
        task_parameters = self._get_dag_task_parameters_from_dynamodb(dag, task)

        dag_parameters = self._override_dag_parameters(dag_parameters, task_parameters)

        if task != "DAG":
            dag_parameters["task"] = task

        return dag_parameters

    @classmethod
    def _override_dag_parameters(cls, dag_parameters, task_parameters):
        for key, _ in task_parameters.items():
            if key in dag_parameters:
                dag_parameters[key] = task_parameters[key]

        return dag_parameters

class DAGTaskWrapper(aws.DAGTaskWrapper):
    def _get_runtime_parameters(self, parameters):
        LOGGER.debug('Event Parameters: %s', parameters)

        return self._supplement_runtime_parameters(parameters)
