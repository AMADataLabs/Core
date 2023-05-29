""" DAG task wrapper and runner classes. """
import logging

from   datalabs.access.environment import VariableTree
from   datalabs.etl.dag.cache import CacheDirection, TaskDataCacheParameters, TaskDataCacheFactory
from   datalabs.etl.dag.notify.email import StatusEmailNotifier
from   datalabs.etl.dag.notify.webhook import StatusWebHookNotifier
from   datalabs.etl.dag.state import Status
from   datalabs.plugin import import_plugin
from   datalabs.task import TaskWrapper

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class DAGTaskWrapper(TaskWrapper):
    def __init__(self, parameters=None):
        super().__init__(parameters)

        self._cache_parameters = {}

    def _get_runtime_parameters(self, parameters):
        return self._parse_command_line_parameters(parameters)

    def _get_task_parameters(self):
        task_parameters = None

        default_parameters = self._get_default_parameters()

        task_parameters = self._merge_parameters(default_parameters, self._get_dag_task_parameters())

        task_parameters, self._cache_parameters = TaskDataCacheParameters.extract(task_parameters)
        LOGGER.debug('Task Parameters: %s', task_parameters)

        return task_parameters

    def _get_task_data(self):
        data = []
        cache = TaskDataCacheFactory.create_cache(CacheDirection.INPUT, self._cache_parameters)

        if cache:
            data = cache.extract_data()

        return data

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

    @classmethod
    def _parse_command_line_parameters(cls, command_line_parameters):
        dag, task, execution_time = command_line_parameters[1].split('__')

        return dict(
            dag=dag,
            task=task,
            execution_time=execution_time
        )

    def _get_default_parameters(self):
        dag_parameters = self._get_default_parameters_from_environment(self._get_dag_id())
        execution_time = self._get_execution_time()

        dag_parameters['EXECUTION_TIME'] = execution_time
        dag_parameters['CACHE_EXECUTION_TIME'] = execution_time

        return dag_parameters

    def _get_dag_task_parameters(self):
        return self._get_task_parameters_from_environment(self._get_dag_id(), self._get_task_id())

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

        self._notify_dag()

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

        self._notify_dag()

        LOGGER.exception(
            'An exception occured while attempting to run task %s of DAG %s.',
            self._get_task_id(),
            self._get_dag_id()
        )

    def _get_dag_name(self):
        base_name, _ = self._parse_dag_id(self._get_dag_id())

        return base_name

    def _get_dag_index(self):
        _, index = self._parse_dag_id(self._get_dag_id())

        return index

    def _get_dag_id(self):
        return self._runtime_parameters["dag"].upper()

    def _get_task_id(self):
        return self._runtime_parameters["task"].upper()

    def _get_execution_time(self):
        return self._runtime_parameters["execution_time"].upper()

    @classmethod
    def _get_default_parameters_from_environment(cls, dag_id):
        parameters = {}

        try:
            parameters = cls._get_parameters([dag_id.upper()])
        except KeyError:
            pass

        return parameters

    @classmethod
    def _get_task_parameters_from_environment(cls, dag_id, task_id):
        parameters = {}

        try:
            parameters = cls._get_parameters([dag_id.upper(), task_id.upper()])
        except KeyError:
            pass

        return parameters

    @classmethod
    def _parse_dag_id(cls, dag):
        base_name = dag
        iteration = None
        components = dag.split(':')

        if len(components) == 2:
            base_name, iteration = components

        return base_name, iteration

    @classmethod
    def _get_parameters(cls, branch):
        var_tree = VariableTree.from_environment()

        candidate_parameters = var_tree.get_branch_values(branch)

        return {key:value for key, value in candidate_parameters.items() if value is not None}

    def _send_dag_status_notification(self, status):
        self._send_email_notification(status)

        self._send_webhook_notification(status)

    def _invoke_triggered_tasks(self, dag):
        for task in dag.triggered_tasks:
            self._notify_task(task)

    def _notify_dag(self):
        pass

    def _notify_task(self, task):
        pass

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
