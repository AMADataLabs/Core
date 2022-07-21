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
        sns_topic = self._get_sns_event_topic(parameters)
        LOGGER.debug('SNS Event Topic: %s', sns_topic)

        event_parameters = self._get_sns_event_parameters(parameters)
        LOGGER.debug('SNS Event Parameters: %s', event_parameters)

        if sns_topic.startswith('DataLake-Scheduler-'):
            event_parameters = self._get_scheduler_event_parameters(event_parameters)

        if "task" not in event_parameters:
            event_parameters["task"] = "DAG"

        return event_parameters

    @classmethod
    def _get_sns_event_topic(cls, parameters):
        return parameters["Records"][0]["Sns"]["TopicArn"].rsplit(':', 1)[1]

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

    def _get_scheduler_event_parameters(self, event_parameters):
        ''' Return appropriate parameters for the DAG Processor assuming the DAG Scheduler as the DAG to execute.'''
        return dict(
            dag="DAG_SCHEDULER",
            execution_time=self.execution_time.isoformat()
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
        dag_name = self._get_dag_name()
        task = self._get_task_id()
        dag_parameters = dict(
            dag=dag,
            execution_time=self._get_execution_time(),
        )
        dag_parameters.update(self._get_dag_task_parameters_from_dynamodb(dag_name, "DAG"))
        task_parameters = self._get_dag_task_parameters_from_dynamodb(dag_name, task)

        dag_parameters = self._override_dag_parameters(dag_parameters, task_parameters)

        if "parameters" in self._runtime_parameters:
            dag_parameters["parameters"] = self._runtime_parameters["parameters"]

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
