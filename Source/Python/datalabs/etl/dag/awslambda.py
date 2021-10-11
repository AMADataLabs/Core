""" Task wrapper for DAG and DAG task Lambda functions. """
from   dataclasses import dataclass
import json
import logging
import os
from   dateutil.parser import isoparse
import urllib.parse

from   datalabs.access.parameter.dynamodb import DynamoDBEnvironmentLoader
from   datalabs.etl.task import ExecutionTimeMixin
from   datalabs.etl.dag.notify.sns import SNSDAGNotifier
from   datalabs.etl.dag.notify.sns import SNSTaskNotifier
from   datalabs.etl.dag.state import Status
from   datalabs.etl.dag.plugin import PluginExecutorMixin
import datalabs.etl.dag.task
from   datalabs.parameter import add_schema, ParameterValidatorMixin

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
        execution_time = urllib.parse.unquote(escaped_execution_time)

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
        LOGGER.error('Handling DAG task exception: %s', exception)

        return f'Failed: {str(exception)}'

    def _get_dag_task_parameters(self):
        ''' Get parameters for either the DAG Processor or the Task Processor. '''
        dag = self._get_dag_id()
        task = self._get_task_id()
        dag_parameters = dict(
            dag=dag,
            execution_time=self._get_execution_time(),
        )
        task_parameters = self._get_dag_task_parameters_from_dynamodb(dag, task)

        dag_parameters.update(self._get_dag_task_parameters_from_dynamodb(dag, "DAG"))

        dag_parameters["LAMBDA_FUNCTION"] = task_parameters.get("LAMBDA_FUNCTION", dag_parameters["LAMBDA_FUNCTION"])

        if task != "DAG":
            dag_parameters["task"] = task

        return dag_parameters


@add_schema(unknowns=True)
@dataclass
class DAGTaskWrapperParameters:
    dag: str
    task: str
    execution_time: str
    unknowns: dict=None


class DAGTaskWrapper(
    DynamoDBTaskParameterGetterMixin,
    ParameterValidatorMixin,
    PluginExecutorMixin,
    datalabs.etl.dag.task.DAGTaskWrapper
):
    PARAMETER_CLASS = DAGTaskWrapperParameters
    DAG_PARAMETERS = None

    @classmethod
    def _get_runtime_parameters(cls, parameters):
        LOGGER.info('Event Parameters: %s', parameters)
        cls.DAG_PARAMETERS = cls._get_dag_task_parameters_from_dynamodb(parameters["dag"], "DAG")

        parameters["dag_class"] = cls.DAG_PARAMETERS["DAG_CLASS"]

        if "task" not in parameters:
            parameters["task"] = "DAG"

        return parameters

    def _handle_success(self) -> (int, dict):
        super()._handle_success()

        parameters = self._runtime_parameters
        parameters.update(self.DAG_PARAMETERS)
        parameters = self._get_validated_parameters(parameters)

        if parameters.task == "DAG":
            for task in self.task.triggered_tasks:
                self._notify_task_processor(task)
        else:
            state = self._get_plugin(self.DAG_PARAMETERS["DAG_STATE_CLASS"], parameters)

            state.set_task_status(parameters.dag, parameters.task, parameters.execution_time, Status.FINISHED)

            self._notify_dag_processor()

        return "Success"

    def _handle_exception(self, exception) -> (int, dict):
        super()._handle_exception(exception)

        parameters = self._runtime_parameters
        parameters.update(self.DAG_PARAMETERS)
        parameters = self._get_validated_parameters(parameters)

        if parameters.task != "DAG":
            state = self._get_plugin(self.DAG_PARAMETERS["DAG_STATE_CLASS"], parameters)

            state.set_task_status(parameters.dag, parameters.task, parameters.execution_time, Status.FAILED)

            self._notify_dag_processor()

        LOGGER.error('Handling DAG task exception: %s', exception)

        return f'Failed: {str(exception)}'

    def _get_dag_task_parameters(self):
        dag = self._get_dag_id()
        task = self._get_task_id()
        LOGGER.debug('Getting DAG Task Parameters for %s__%s...', dag, task)
        dag_task_parameters = self._get_dag_task_parameters_from_dynamodb(dag, task)
        LOGGER.debug('Raw DAG Task Parameters: %s', dag_task_parameters)

        if task == 'DAG':
            dag_task_parameters["dag"] = dag
        elif "LAMBDA_FUNCTION" in dag_task_parameters:
            dag_task_parameters.pop("LAMBDA_FUNCTION")
        LOGGER.debug('Final DAG Task Parameters: %s', dag_task_parameters)

        return dag_task_parameters

    def _notify_task_processor(self, task):
        task_topic = self._runtime_parameters["TASK_TOPIC_ARN"]
        notifier = SNSTaskNotifier(task_topic)

        notifier.notify(self._get_dag_id(), task, self._get_execution_time())

    def _notify_dag_processor(self):
        dag_topic = self._runtime_parameters["DAG_TOPIC_ARN"]
        notifier = SNSDAGNotifier(dag_topic)

        notifier.notify(self._get_dag_id(), self._get_execution_time())
