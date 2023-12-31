""" Event-driven DAG classes """
from   abc import abstractmethod
import json
import logging

from   datalabs.etl.dag.notify.email import StatusEmailNotifier
from   datalabs.etl.dag.notify.webhook import StatusWebHookNotifier
from   datalabs.etl.dag.state import Status, StatefulDAGMixin
from   datalabs.task import Task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class EventDrivenDAGMixin(StatefulDAGMixin):
    def _handle_dag_success(self, dag):
        dag_state = self._get_state_plugin(self._task_parameters)

        self._update_dag_status_on_success(dag, dag_state)

        LOGGER.debug("%d tasks ready to run.", len(dag.triggered_tasks))
        for task in dag.triggered_tasks:
            self._notify_task(task)

    def _handle_task_success(self, task):
        dag_state = self._get_state_plugin(self._task_parameters)

        if dag_state:
            self._update_task_status_on_success(task, dag_state)

        self._notify_dag()

    def _handle_dag_exception(self, dag):
        dag_state = self._get_state_plugin(self._task_parameters)

        if dag_state:
            self._update_dag_status_on_exception(dag, dag_state)

    def _handle_task_exception(self, task):
        dag_state = self._get_state_plugin(self._task_parameters)

        if dag_state:
            self._update_task_status_on_exception(task, dag_state)

        self._notify_dag()

        LOGGER.exception(
            'An exception occured while attempting to run task %s of DAG %s.',
            self._get_task_id(),
            self._get_dag_id()
        )

    def _handle_task_not_ready(self, task):
        dag_state = self._get_state_plugin(self._task_parameters)
        dag = self._get_dag_id()
        execution_time = self._get_execution_time()

        if dag_state:
            dag_state.pause_dag(dag, task, execution_time)

    def _update_dag_status_on_success(self, dag, dag_state):
        dag_id = self._get_dag_id()
        execution_time = self._get_execution_time()
        current_status = dag_state.get_dag_status(dag_id, execution_time)
        LOGGER.debug('Current DAG "%s" status is %s and should be %s.', dag_id, current_status, dag.status)

        if current_status != dag.status:
            success = dag_state.set_dag_status(dag_id, execution_time, dag.status)
            LOGGER.info( 'Setting status of DAG "%s" (%s) to %s', dag_id, execution_time, dag.status)

            if not success:
                LOGGER.error('Unable to set status of DAG %s to Finished', dag_id)

            if dag.status in [Status.FINISHED, Status.FAILED]:
                self._send_dag_status_notification(dag.status)

    def _update_task_status_on_success(self, task, dag_state):
        dag = self._get_dag_id()
        task = self._get_task_id()
        execution_time = self._get_execution_time()

        success = dag_state.set_task_status(dag, task, execution_time, Status.FINISHED)

        if not success:
            LOGGER.error('Unable to set status of task %s of dag %s to Finished', task, dag)

    def _update_dag_status_on_exception(self, dag, dag_state):
        dag_id = self._get_dag_id()
        execution_time = self._get_execution_time()
        current_status = dag_state.get_dag_status(dag_id, execution_time)

        if current_status not in [Status.FINISHED, Status.FAILED]:
            success = dag_state.set_dag_status(dag_id, execution_time, Status.FAILED)
            LOGGER.info( 'Setting status of dag "%s" (%s) to %s', dag_id, execution_time, Status.FAILED)

            if not success:
                LOGGER.error('Unable to set status of of dag %s to Failed', dag)

            self._send_dag_status_notification(Status.FAILED)

    def _update_task_status_on_exception(self, task, dag_state):
        dag = self._get_dag_id()
        task = self._get_task_id()
        execution_time = self._get_execution_time()

        success = dag_state.set_task_status(dag, task, execution_time, Status.FAILED)

        if not success:
            LOGGER.error('Unable to set status of task %s of dag %s to Failed', task, dag)

    def _send_dag_status_notification(self, status):
        self._send_email_notification(status)

        self._send_webhook_notification(status)

    def _send_email_notification(self, status):
        raw_email_list = self._task_parameters.get("STATUS_NOTIFICATION_EMAILS")
        LOGGER.info('EMAIL LIST %s', raw_email_list)
        if raw_email_list is not None:
            emails = raw_email_list.split(',')
            environment = self._task_parameters.get("ENVIRONMENT")
            from_account = self._task_parameters.get("STATUS_NOTIFICATION_FROM")
            notifier = StatusEmailNotifier(emails, environment, from_account)

            notifier.notify(self._get_dag_id(), self._get_execution_time(), status)

    def _send_webhook_notification(self, status):
        raw_webhook_url_list = self._task_parameters.get("STATUS_NOTIFICATION_WEB_HOOK")
        LOGGER.info('WEB HOOK LIST %s', raw_webhook_url_list)
        if raw_webhook_url_list is not None:
            urls = raw_webhook_url_list.split(',')
            environment = self._task_parameters.get("ENVIRONMENT")
            notifier = StatusWebHookNotifier(urls, environment)
            notifier.notify(self._get_dag_id(), self._get_execution_time(), status)

class ExternalConditionPollingTask(Task):
    def __init__(self, parameters: dict, data: "list<bytes>"=None):
        super().__init__(parameters, data)
        self._request_parameters = None

    def run(self):
        self._request_parameters = json.loads(self._data[0])

        if not self._is_ready():
            raise TaskNotReady('Task is not ready to finish.')

        return [json.dumps(self._create_results_parameters()).encode()]

    @abstractmethod
    def _is_ready(self):
        pass

    def _create_results_parameters(self):
        return self._request_parameters


class TaskNotReady(Exception):
    pass
