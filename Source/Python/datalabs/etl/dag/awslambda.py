""" Task wrapper for DAG and DAG task Lambda functions. """
import json
import logging
import re

from   dateutil.parser import isoparse

from   datalabs.access.parameter.dynamodb import DynamoDBTaskParameterGetterMixin
from   datalabs.etl.task import ExecutionTimeMixin, TaskWrapper
from   datalabs.etl.dag import aws
from   datalabs.etl.dag.task import DAGTaskIDMixin

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class ProcessorTaskWrapper(
    ExecutionTimeMixin,
    DAGTaskIDMixin,
    DynamoDBTaskParameterGetterMixin,
    TaskWrapper
):
    def _get_task_parameters(self):
        LOGGER.debug('Event: %s', self._parameters)
        topic = self._extract_topic_base_name(self._parameters)
        event_parameters = self._get_sns_event_parameters(self._parameters)
        task_parameters = None

        if topic not in ("DAGProcessor", "TaskProcessor"):
            event_parameters = self._get_trigger_event_parameters(event_parameters, topic)
        LOGGER.debug('Event Parameters: %s', event_parameters)

        if "task" in event_parameters:
            task_parameters = self._get_task_processor_parameters(event_parameters)
        elif "dag" in event_parameters:
            task_parameters = self._get_dag_processor_parameters(event_parameters)
        else:
            task_parameters = self._get_trigger_processor_parameters(event_parameters)

        return task_parameters

    def _handle_success(self) -> (int, dict):
        return "Success"

    def _handle_exception(self, exception) -> (int, dict):
        LOGGER.exception('An exception occured while running the processor.')

        return f'Failed: {str(exception)}'

    @classmethod
    def _extract_topic_base_name(cls, parameters):
        sns_topic = cls._get_sns_event_topic(parameters)
        LOGGER.debug('SNS Event Topic: %s', sns_topic)
        topic_parts = re.match(r'(?P<stack>..*)-(?P<environment>[a-z]{3})-(?P<name>..*)', sns_topic)

        if topic_parts.group("stack") != "DataLake":
            raise ValueError(f"Unrecognized SNS topic: {sns_topic}")

        return topic_parts.group("name")

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

        event_parameters = json.loads(record["Sns"]["Message"])

        if "execution_time" not in event_parameters:
            event_parameters["execution_time"] = cls._format_execution_time(record["Sns"]["Timestamp"])

        return event_parameters

    @classmethod
    def _get_trigger_event_parameters(cls, event_parameters, topic_name):
        handler_parameters = cls._get_dag_task_parameters_from_dynamodb("TRIGGER_PROCESSOR", "HANDLER")
        trigger_parameters = cls._get_dag_task_parameters_from_dynamodb("TRIGGER_PROCESSOR", topic_name)

        return dict(
            handler_class=trigger_parameters["HANDLER_CLASS"],
            dag_topic_arn=handler_parameters["DAG_TOPIC_ARN"],
            event=event_parameters
        )

    def _get_task_processor_parameters(self, event_parameters):
        dag_id = event_parameters["dag"].upper()
        dag, _ = self._parse_dag_id(dag_id)
        task = event_parameters["task"].upper()

        dag_parameters = self._get_dag_processor_parameters(event_parameters)

        task_parameters = self._get_dag_task_parameters_from_dynamodb(dag, task)

        task_parameters = self._merge_parameters(dag_parameters, task_parameters)

        task_parameters["task"] = task

        return task_parameters

    def _get_dag_processor_parameters(self, event_parameters):
        dag_id = event_parameters["dag"].upper()
        dag, _ = self._parse_dag_id(dag_id)
        dag_parameters = dict(
            dag=dag,
            execution_time=event_parameters["execution_time"].upper(),
        )
        dag_parameters.update(self._get_dag_task_parameters_from_dynamodb(dag, "DAG"))

        if "parameters" in event_parameters:
            dag_parameters["parameters"] = event_parameters["parameters"]

        return dag_parameters

    def _get_trigger_processor_parameters(self, event_parameters):
        return event_parameters

    @classmethod
    def _format_execution_time(cls, timestamp: str):
        return isoparse(timestamp).strftime("%Y-%m-%dT%H:%M:%S")


class DAGTaskWrapper(aws.DAGTaskWrapper):
    def _get_dag_parameters(self, parameters):
        dag_parameters = parameters
        dag_id = dag_parameters["dag"].upper()
        dag, _ = self._parse_dag_id(dag_id)
        LOGGER.debug('Event Parameters: %s', dag_parameters)

        dag_parameters.update(self._get_dag_task_parameters_from_dynamodb(dag, "DAG"))

        if "task" not in dag_parameters:
            dag_parameters["task"] = "DAG"

        LOGGER.debug('DAG Parameters: %s', dag_parameters)

        return dag_parameters
