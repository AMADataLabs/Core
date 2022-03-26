""" Task wrapper for DAGs and DAG tasks running in AWS. """
from   dataclasses import dataclass
import logging
import os

from   datalabs.access.parameter.dynamodb import DynamoDBEnvironmentLoader
from   datalabs.etl.dag.notify.sns import SNSDAGNotifier
from   datalabs.etl.dag.notify.sns import SNSTaskNotifier
from   datalabs.etl.dag.notify.email import StatusEmailNotifier
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

    def _get_runtime_parameters(self, parameters):
        command_line_parameters = super()._get_runtime_parameters(parameters)
        LOGGER.info('Event Parameters: %s', parameters)
        runtime_parameters = self._get_dag_parameters()

        runtime_parameters.update(command_line_parameters)

        return runtime_parameters

    def _pre_run(self):
        super()._pre_run()

        parameters = self._get_task_wrapper_parameters()

        if parameters.task != "DAG":
            state = self._get_plugin(self.DAG_PARAMETERS["DAG_STATE_CLASS"], parameters)

            state.set_task_status(parameters.dag, parameters.task, parameters.execution_time, Status.RUNNING)

    def _handle_success(self) -> (int, dict):
        super()._handle_success()

        parameters = self._get_task_wrapper_parameters()

        if parameters.task == "DAG":
            for task in self.task.triggered_tasks:
                self._notify_task_processor(task)

            if self.task.status in [Status.FINISHED, Status.FAILED]:
                self._send_status_notification()
        else:
            state = self._get_plugin(self.DAG_PARAMETERS["DAG_STATE_CLASS"], parameters)

            success = state.set_task_status(parameters.dag, parameters.task, parameters.execution_time, Status.FINISHED)

            if not success:
                LOGGER.error('Unable to set status of task %s of dag %s to Finished', parameters.task, parameters.dag)

            self._notify_dag_processor()

        return "Success"

    def _handle_exception(self, exception) -> (int, dict):
        super()._handle_exception(exception)

        parameters = self._get_task_wrapper_parameters()

        if parameters.task != "DAG":
            state = self._get_plugin(self.DAG_PARAMETERS["DAG_STATE_CLASS"], parameters)

            success = state.set_task_status(parameters.dag, parameters.task, parameters.execution_time, Status.FAILED)

            if not success:
                LOGGER.error('Unable to set status of task %s of dag %s to Failed', parameters.task, parameters.dag)

            self._notify_dag_processor()

        LOGGER.exception(
            'An exception occured while attempting to run task %s of DAG %s.',
            self._get_task_id(),
            self._get_dag_id()
        )

        return f'Failed: {str(exception)}'

    def _get_dag_parameters(self):
        dag = self._get_dag_id()
        LOGGER.debug('Getting DAG Parameters for %s...', dag)
        dag_parameters = self._get_dag_task_parameters_from_dynamodb(dag, "DAG")
        LOGGER.debug('Raw DAG Parameters: %s', dag_parameters)

        return dag_parameters

    def _get_dag_task_parameters(self):
        dag = self._get_dag_id()
        task = self._get_task_id()
        LOGGER.debug('Getting DAG Task Parameters for %s__%s...', dag, task)
        dag_task_parameters = self._get_dag_task_parameters_from_dynamodb(dag, task)

        if task == 'DAG':
            dag_task_parameters["dag"] = dag
        else:
            dag_task_parameters = self._override_runtime_parameters(dag_task_parameters)
        LOGGER.debug('Final DAG Task Parameters: %s', dag_task_parameters)

        return dag_task_parameters

    def _get_task_wrapper_parameters(self):
        return self._get_validated_parameters(self._runtime_parameters)

    def _notify_task_processor(self, task):
        task_topic = self._runtime_parameters["TASK_TOPIC_ARN"]
        notifier = SNSTaskNotifier(task_topic)

        notifier.notify(self._get_dag_id(), task, self._get_execution_time())

    def _notify_dag_processor(self):
        dag_topic = self._runtime_parameters["DAG_TOPIC_ARN"]
        notifier = SNSDAGNotifier(dag_topic)

        notifier.notify(self._get_dag_id(), self._get_execution_time())

    def _send_status_notification(self):
        raw_email_list = self._runtime_parameters.get("STATUS_NOTIFICATION_EMAILS")

        if raw_email_list is not None:
            emails = raw_email_list.split(',')
            environment = self._runtime_parameters.get("ENVIRONMENT")
            from_account = self._runtime_parameters.get("STATUS_NOTIFICATION_FROM")
            notifier = StatusEmailNotifier(emails, environment, from_account)

            notifier.notify(self._get_dag_id(), self._get_execution_time(), self.task.status)

    def _override_runtime_parameters(self, task_parameters):
        for name, value in task_parameters.iteritems():
            if name in self._runtime_parameters:
                self._runtime_parameters[name] = value
                task_parameters.pop(name)

        return task_parameters
