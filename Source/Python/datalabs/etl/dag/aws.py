""" Task wrapper for DAGs and DAG tasks running in AWS. """
from   dataclasses import dataclass
import logging
import os

from   datalabs.access.parameter.dynamodb import DynamoDBEnvironmentLoader
from   datalabs.etl.dag.notify.sns import SNSDAGNotifier
from   datalabs.etl.dag.notify.sns import SNSTaskNotifier
from   datalabs.etl.dag.notify.email import StatusEmailNotifier
from   datalabs.etl.dag.state import Status
from   datalabs.plugin import import_plugin
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
    datalabs.etl.dag.task.DAGTaskWrapper
):
    PARAMETER_CLASS = DAGTaskWrapperParameters

    def _get_runtime_parameters(self, parameters):
        command_line_parameters = self._parse_command_line_parameters(parameters)
        LOGGER.debug('Command-line Parameters: %s', command_line_parameters)

        return self._supplement_runtime_parameters(command_line_parameters)

    def _pre_run(self):
        super()._pre_run()
        dag = self._get_dag_id() + ":" + self._get_dag_index()
        task = self._get_task_id()
        execution_time = self._get_execution_time()

        if task != "DAG":
            state = import_plugin(self._runtime_parameters["DAG_STATE_CLASS"])(self._runtime_parameters)

            state.set_task_status(dag, task, execution_time, Status.RUNNING)

    def _handle_success(self) -> str:
        super()._handle_success()

        if self._get_task_id() == "DAG":
            self._handle_dag_success(self.task)
        else:
            self._handle_task_success(self.task)

        return "Success"

    def _handle_exception(self, exception) -> str:
        super()._handle_exception(exception)

        if self._get_task_id() == "DAG":
            self._handle_dag_exception(self.task)
        else:
            self._handle_task_exception(self.task)

        return f'Failed: {str(exception)}'

    def _get_dag_task_parameters(self):
        dag = self._get_dag_id()
        task = self._get_task_id()
        LOGGER.debug('Getting DAG Task Parameters for %s__%s...', dag, task)
        dag_task_parameters = self._get_dag_task_parameters_from_dynamodb(dag, task)

        if task != 'DAG':
            dag_task_parameters = self._override_runtime_parameters(dag_task_parameters)

            dag_task_parameters = self._remove_bootstrap_parameters(dag_task_parameters)
        LOGGER.debug('Final DAG Task Parameters: %s', dag_task_parameters)

        return dag_task_parameters

    def _get_task_wrapper_parameters(self):
        return self._get_validated_parameters(self._runtime_parameters)

    def _supplement_runtime_parameters(self, runtime_parameters):
        dag_id = runtime_parameters["dag"].upper()
        dag_base_name, _ = self._parse_dag_id(dag_id)
        dag_parameters = self._get_dag_parameters(dag_base_name)
        LOGGER.debug('DAG Parameters: %s', dag_parameters)

        runtime_parameters.update(dag_parameters)
        LOGGER.debug('Runtime Parameters: %s', runtime_parameters)

        if "task" not in runtime_parameters:
            runtime_parameters["task"] = "DAG"

            state = import_plugin(self._runtime_parameters["DAG_STATE_CLASS"])(runtime_parameters)
            runtime_parameters["task_statuses"] = state.get_all_statuses(dag_id, runtime_parameters["execution_time"])

        return runtime_parameters

    def _override_runtime_parameters(self, task_parameters):
        for name, value in list(task_parameters.items()):
            if name in self._runtime_parameters:
                self._runtime_parameters[name] = value
                task_parameters.pop(name)

        return task_parameters

    @classmethod
    def _remove_bootstrap_parameters(cls, task_parameters):
        if 'TASK_CLASS' in task_parameters:
            task_parameters.pop("TASK_CLASS")

        return task_parameters

    def _get_dag_parameters(self, dag):
        LOGGER.debug('Getting DAG Parameters for %s...', dag)
        dag_parameters = self._get_dag_task_parameters_from_dynamodb(dag, "DAG")
        LOGGER.debug('Raw DAG Parameters: %s', dag_parameters)

        return dag_parameters

    def _handle_dag_success(self, dag):
        dag_id = self._get_dag_id()
        execution_time = self._get_execution_time()
        state = import_plugin(self._runtime_parameters["DAG_STATE_CLASS"])(self._runtime_parameters)
        current_status = state.get_dag_status(dag_id, execution_time)

        if current_status != dag.status:
            success = state.set_dag_status(dag_id, execution_time, dag.status)
            LOGGER.info( 'Setting status of dag "%s" (%s) to %s', dag_id, execution_time, dag.status)

            if not success:
                LOGGER.error('Unable to set status of dag %s to Finished', dag_id)

            if dag.status in [Status.FINISHED, Status.FAILED]:
                self._send_dag_status_notification(dag.status)

        self._invoke_triggered_tasks(dag)

    def _handle_task_success(self, task):
        dag = self._get_dag_id()
        task = self._get_task_id()
        execution_time = self._get_execution_time()
        state = import_plugin(self._runtime_parameters["DAG_STATE_CLASS"])(self._runtime_parameters)

        success = state.set_task_status(dag, task, execution_time, Status.FINISHED)

        if not success:
            LOGGER.error('Unable to set status of task %s of dag %s to Finished', task, dag)

        self._notify_dag_processor()

    def _handle_dag_exception(self, dag):
        dag_id = self._get_dag_id()
        execution_time = self._get_execution_time()
        state = import_plugin(self._runtime_parameters["DAG_STATE_CLASS"])(self._runtime_parameters)
        current_status = state.get_dag_status(dag_id, execution_time)

        if current_status not in [Status.FINISHED, Status.FAILED]:
            success = state.set_dag_status(dag_id, execution_time, Status.FAILED)
            LOGGER.info( 'Setting status of dag "%s" (%s) to %s', dag_id, execution_time, Status.FAILED)

            if not success:
                LOGGER.error('Unable to set status of of dag %s to Failed', dag)

            self._send_dag_status_notification(Status.FAILED)

    def _handle_task_exception(self, task):
        dag = self._get_dag_id()
        task = self._get_task_id()
        execution_time = self._get_execution_time()
        state = import_plugin(self._runtime_parameters["DAG_STATE_CLASS"])(self._runtime_parameters)

        success = state.set_task_status(dag, task, execution_time, Status.FAILED)

        if not success:
            LOGGER.error('Unable to set status of task %s of dag %s to Failed', task, dag)

        self._notify_dag_processor()

        LOGGER.exception(
            'An exception occured while attempting to run task %s of DAG %s.',
            self._get_task_id(),
            self._get_dag_id()
        )

    def _send_dag_status_notification(self, status):
        raw_email_list = self._runtime_parameters.get("STATUS_NOTIFICATION_EMAILS")

        if raw_email_list is not None:
            emails = raw_email_list.split(',')
            environment = self._runtime_parameters.get("ENVIRONMENT")
            from_account = self._runtime_parameters.get("STATUS_NOTIFICATION_FROM")
            notifier = StatusEmailNotifier(emails, environment, from_account)

            notifier.notify(self._get_dag_id(), self._get_execution_time(), status)

    def _invoke_triggered_tasks(self, dag):
        for task in dag.triggered_tasks:
            self._notify_task_processor(task)

    def _notify_dag_processor(self):
        dag_topic = self._runtime_parameters["DAG_TOPIC_ARN"]
        notifier = SNSDAGNotifier(dag_topic)

        notifier.notify(self._get_dag_id(), self._get_execution_time())

    def _notify_task_processor(self, task):
        task_topic = self._runtime_parameters["TASK_TOPIC_ARN"]
        notifier = SNSTaskNotifier(task_topic)

        notifier.notify(self._get_dag_id(), task, self._get_execution_time())
