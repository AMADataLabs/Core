import os
from   dataclasses import dataclass
import logging
import json

from   datalabs.access.parameter.file import FileEnvironmentLoader
from   datalabs.access.parameter.system import ReferenceEnvironmentLoader
from   datalabs.etl.dag.notify.celery import CeleryDAGNotifier, CeleryTaskNotifier
from   datalabs.parameter import add_schema, ParameterValidatorMixin
from   datalabs.etl.dag.notify.email import StatusEmailNotifier
from   datalabs.etl.dag.notify.webhook import StatusWebHookNotifier
import datalabs.etl.dag.task
from   datalabs.etl.dag.state import Status
from   datalabs.plugin import import_plugin

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

class FileTaskParameterGetterMixin:
    @classmethod
    def _get_dag_task_parameters_from_file(cls, dag: str, task: str, config_file: str):
        file_loader = FileEnvironmentLoader(dict(
            dag=dag,
            task=task,
            path=config_file
        ))
        parameters = file_loader.load()

        return parameters


class CeleryProcessorNotifierMixin:
    def _notify_dag_processor(self):
        dynamic_parameters = dict(
            config_file=self._runtime_parameters["config_file"]
        )
        if "parameters" in self._runtime_parameters:
            dynamic_parameters.update(self.runtime_parameters["parameters"])
        notifier = CeleryDAGNotifier()
        notifier.notify(self._get_dag_id(), self._get_execution_time(), dynamic_parameters)

    def _notify_task_processor(self, task):
        dynamic_parameters = dict(
            config_file=self._runtime_parameters["config_file"]
        )
        if "parameters" in self._runtime_parameters:
            dynamic_parameters.update(self._runtime_parameters["parameters"])
        notifier = CeleryTaskNotifier()
        notifier.notify(self._get_dag_id(), task, self._get_execution_time(), dynamic_parameters)

class DAGTaskWrapper(
    FileTaskParameterGetterMixin,
    CeleryProcessorNotifierMixin,
    ParameterValidatorMixin,
    datalabs.etl.dag.task.DAGTaskWrapper
):

    def _get_runtime_parameters(self, parameters):
        return self._supplement_runtime_parameters(parameters)

    def _pre_run(self):
        super()._pre_run()
        dag = self._get_dag_id()
        task = self._get_task_id()
        execution_time = self._get_execution_time()
        path = self._runtime_parameters["config_file"]

        if task != "LOCAL":
            state = import_plugin(self._runtime_parameters["DAG_STATE_CLASS"])(self._runtime_parameters)

            success = state.set_task_status(dag, task, execution_time, Status.RUNNING)

            if not success:
                LOGGER.error('Unable to set status of task %s of dag %s to Running', task, dag)

    def _handle_success(self) -> str:
        super()._handle_success()
        if self._get_task_id() == "LOCAL":
            self._handle_dag_success(self.task)
        else:
            self._handle_task_success(self.task)

        return "Success"

    def _handle_exception(self, exception) -> str:
        super()._handle_exception(exception)

        if self._get_task_id() == "LOCAL":
            self._handle_dag_exception(self.task)
        else:
            self._handle_task_exception(self.task)

        return f'Failed: {str(exception)}'

    def _get_dag_task_parameters(self):
        dag_id = self._get_dag_id()
        dag_name = self._get_dag_name()
        task = self._get_task_id()
        execution_time = self._get_execution_time()
        config_file_path = self._parameters["config_file"]
        dag_task_parameters = self._get_dag_task_parameters_from_file(dag_name, task, config_file_path)
        LOGGER.debug('Raw DAG Task Parameters: %s', dag_task_parameters)
        dynamic_parameters = self._runtime_parameters.get("parameters", {})
        LOGGER.debug('Dynamic DAG Task Parameters: %s', dynamic_parameters)

        if task == 'LOCAL':
            state = import_plugin(self._runtime_parameters["DAG_STATE_CLASS"])(self._runtime_parameters)
            dag_task_parameters["task_statuses"] = state.get_all_statuses(dag_id, execution_time)

        else:
            dag_task_parameters = self._override_runtime_parameters(dag_task_parameters)
            dag_task_parameters = self._remove_bootstrap_parameters(dag_task_parameters)
            
        LOGGER.debug('Pre-dynamic resolution DAG Task Parameters: %s', dag_task_parameters)
        dynamic_loader = ReferenceEnvironmentLoader(dynamic_parameters)
        dynamic_loader.load(environment=dag_task_parameters)

        LOGGER.debug('Final DAG Task Parameters: %s', dag_task_parameters)

        return dag_task_parameters

    def _get_task_wrapper_parameters(self):
        return self._get_validated_parameters(self._runtime_parameters)

    def _supplement_runtime_parameters(self, runtime_parameters):
        dag_id = runtime_parameters["dag"].upper()
        dag_name, _ = self._parse_dag_id(dag_id)
        path = runtime_parameters["config_file"]
        dag_parameters = self._get_dag_parameters(dag_name, path)
        LOGGER.debug('DAG Parameters: %s', dag_parameters)

        runtime_parameters.update(dag_parameters)

        if "task" not in runtime_parameters:
            runtime_parameters["task"] = "LOCAL"

        LOGGER.debug('Runtime Parameters: %s', runtime_parameters)

        return runtime_parameters

    def _override_runtime_parameters(self, task_parameters):
        print(task_parameters)
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

    def _get_dag_parameters(self, dag, path):
        LOGGER.debug('Getting DAG Parameters for %s...', dag)
        dag_parameters = self._get_dag_task_parameters_from_file(dag, "LOCAL", path)
        LOGGER.debug('Raw DAG Parameters: %s', dag_parameters)

        return dag_parameters

    def _handle_dag_success(self, dag):
        dag_id = self._get_dag_id()
        execution_time = self._get_execution_time()
        state = import_plugin(self._runtime_parameters["DAG_STATE_CLASS"])(self._runtime_parameters)
        current_status = state.get_dag_status(dag_id, execution_time)
        LOGGER.debug('Current DAG "%s" status is %s and should be %s.', dag_id, current_status, dag.status)

        if current_status != dag.status:
            success = state.set_dag_status(dag_id, execution_time, dag.status)
            LOGGER.info( 'Setting status of DAG "%s" (%s) to %s', dag_id, execution_time, dag.status)
            if not success:
                LOGGER.error('Unable to set status of DAG %s to Finished', dag_id)

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
        self._send_email_notification(status)
        self._send_webhook_notification(status)

    def _invoke_triggered_tasks(self, dag):
        for task in dag.triggered_tasks:
            self._notify_task_processor(task)
        

    def _send_email_notification(self, status):
        raw_email_list = self._runtime_parameters.get("STATUS_NOTIFICATION_EMAILS")
        LOGGER.info('EMAIL LIST %s', raw_email_list)
        if raw_email_list is not None:
            emails = raw_email_list.split(',')
            environment = self._runtime_parameters.get("ENVIRONMENT")
            from_account = self._runtime_parameters.get("STATUS_NOTIFICATION_FROM")
            notifier = StatusEmailNotifier(emails, environment, from_account)

            notifier.notify(self._get_dag_id(), self._get_execution_time(), status)

    def _send_webhook_notification(self, status):
        raw_webhook_url_list = self._runtime_parameters.get("STATUS_NOTIFICATION_WEB_HOOK")
        LOGGER.info('WEB HOOK LIST %s', raw_webhook_url_list)
        if raw_webhook_url_list is not None:
            urls = raw_webhook_url_list.split(',')
            environment = self._runtime_parameters.get("ENVIRONMENT")
            notifier = StatusWebHookNotifier(urls, environment)
            notifier.notify(self._get_dag_id(), self._get_execution_time(), status)
