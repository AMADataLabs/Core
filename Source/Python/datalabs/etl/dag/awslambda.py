""" Task wrapper for DAG and DAG task Lambda functions. """
import json
import logging
import re

from   dateutil.parser import isoparse

from   datalabs.access.parameter.dynamodb import DynamoDBTaskParameterGetterMixin
from   datalabs.etl.task import ExecutionTimeMixin
from   datalabs.etl.dag import aws
import datalabs.etl.dag.task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class ProcessorTaskWrapper(
    ExecutionTimeMixin,
    DynamoDBTaskParameterGetterMixin,
    datalabs.etl.task.TaskWrapper
):
    def _get_runtime_parameters(self, parameters):
        LOGGER.debug('Event: %s', parameters)
        sns_topic = self._get_sns_event_topic(parameters)
        LOGGER.debug('SNS Event Topic: %s', sns_topic)
        topic_parts = re.match(r'(?P<stack>..*)-(?P<environment>[a-z]{3})-(?P<name>..*)', sns_topic)
        event_parameters = self._get_sns_event_parameters(parameters)
        runtime_parameters = None

        if topic_parts.group("stack") != "DataLake":
            raise ValueError(f"Unrecognized SNS topic: {sns_topic}")

        if topic_parts.group("name") == "DAGProcessor":
            runtime_parameters = self._get_dag_processor_runtime_parameters(event_parameters)
        elif topic_parts.group("name") == "TaskProcessor":
            runtime_parameters = self._get_task_processor_runtime_parameters(event_parameters)
        else:
            runtime_parameters = self._get_trigger_processor_runtime_parameters(event_parameters, topic_parts["name"])
        LOGGER.debug('Runtime Parameters: %s', event_parameters)

        return runtime_parameters

    def _get_task_parameters(self):
        task_parameters = None

        if "task" in self._runtime_parameters:
            task_parameters = self._get_task_processor_parameters()
        elif "dag" in self._runtime_parameters:
            task_parameters = self._get_dag_processor_parameters()
        else:
            task_parameters = self._get_trigger_processor_parameters()

        return task_parameters

    def _handle_success(self) -> (int, dict):
        return "Success"

    def _handle_exception(self, exception) -> (int, dict):
        LOGGER.exception('An exception occured while running the processor.')

        return f'Failed: {str(exception)}'

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
    def _get_dag_processor_runtime_parameters(cls, event_parameters):
        return event_parameters

    @classmethod
    def _get_task_processor_runtime_parameters(cls, event_parameters):
        return event_parameters

    @classmethod
    def _get_trigger_processor_runtime_parameters(cls, event_parameters, topic_name):
        handler_parameters = cls._get_dag_task_parameters_from_dynamodb("TRIGGER_PROCESSOR", "HANDLER")
        trigger_parameters = cls._get_dag_task_parameters_from_dynamodb("TRIGGER_PROCESSOR", topic_name)

        return dict(
            handler_class=trigger_parameters["HANDLER_CLASS"],
            dag_topic_arn=handler_parameters["DAG_TOPIC_ARN"],
            event=event_parameters
        )

    def _get_task_processor_parameters(self):
        dag_parameters = self._get_dag_processor_parameters()
        dag_name = self._get_dag_name()
        task = self._get_task_id()
        task_parameters = self._get_dag_task_parameters_from_dynamodb(dag_name, task)

        dag_parameters = self._override_dag_parameters(dag_parameters, task_parameters)

        dag_parameters["task"] = task

        return dag_parameters

    def _get_dag_processor_parameters(self):
        dag = self._get_dag_id()
        dag_name = self._get_dag_name()
        dag_parameters = dict(
            dag=dag,
            execution_time=self._get_execution_time(),
        )
        dag_parameters.update(self._get_dag_task_parameters_from_dynamodb(dag_name, "DAG"))

        if "parameters" in self._runtime_parameters:
            dag_parameters["parameters"] = self._runtime_parameters["parameters"]

        return dag_parameters

    def _get_trigger_processor_parameters(self):
        return self._runtime_parameters

    def _get_dag_id(self):
        return self._runtime_parameters["dag"].upper()

    def _get_dag_name(self):
        base_name, _ = self._parse_dag_id(self._get_dag_id())

        return base_name

    def _get_task_id(self):
        return self._runtime_parameters["task"].upper()

    def _get_execution_time(self):
        return self._runtime_parameters["execution_time"].upper()

    @classmethod
    def _format_execution_time(cls, timestamp: str):
        return isoparse(timestamp).strftime("%Y-%m-%dT%H:%M:%S")


    @classmethod
    def _override_dag_parameters(cls, dag_parameters, task_parameters):
        for key, _ in task_parameters.items():
            if key in dag_parameters:
                LOGGER.info("Overriding DAG parameter %s: %s -> %s", key, dag_parameters[key], task_parameters[key])
                dag_parameters[key] = task_parameters[key]

        return dag_parameters

    @classmethod
    def _parse_dag_id(cls, dag):
        base_name = dag
        iteration = None
        components = dag.split(':')

        if len(components) == 2:
            base_name, iteration = components

        return base_name, iteration


class DAGTaskWrapper(aws.DAGTaskWrapper):
    def _get_runtime_parameters(self, parameters):
        LOGGER.debug('Event Parameters: %s', parameters)

        return self._supplement_runtime_parameters(parameters)
