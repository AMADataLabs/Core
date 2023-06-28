""" Task wrapper for a Celery runtime environment. """
import logging

from   datalabs.access.parameter.file import FileTaskParameterGetterMixin
from   datalabs.access.parameter.system import ReferenceEnvironmentLoader
from   datalabs.etl.dag.notify.celery import CeleryDAGNotifier, CeleryTaskNotifier
import datalabs.etl.dag.task
from   datalabs.etl.dag.state import Status

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class CeleryProcessorNotifierMixin:
    def _notify_dag(self):
        dynamic_parameters = dict(
            config_file=self._task_parameters["config_file"]
        )

        if "parameters" in self._task_parameters:
            dynamic_parameters.update(self.runtime_parameters["parameters"])

        CeleryDAGNotifier.notify(self._get_dag_id(), self._get_execution_time(), dynamic_parameters)

    def _notify_task(self, task):
        dynamic_parameters = dict(
            config_file=self._task_parameters["config_file"]
        )

        if "parameters" in self._task_parameters:
            dynamic_parameters.update(self._task_parameters["parameters"])

        CeleryTaskNotifier.notify(self._get_dag_id(), task, self._get_execution_time(), dynamic_parameters)


class DAGTaskWrapper(FileTaskParameterGetterMixin, CeleryProcessorNotifierMixin, datalabs.etl.dag.task.DAGTaskWrapper):
    def _pre_run(self):
        super()._pre_run()
        LOGGER.debug('Pre-dynamic resolution DAG Task Parameters: %s', self._task_parameters)

        self._task_parameters = self._resolve_dynamic_parameters(self._task_parameters)

        LOGGER.debug('Final DAG Task Parameters: %s', self._task_parameters)

        if self._get_task_id() == 'DAG':
            self._start_dag_run()

    def _get_dag_parameters(self):
        dag_parameters = self._parameters
        dag_id = dag_parameters["dag"].upper()
        dag, _ = self._parse_dag_id(dag_id)
        config_file_path = dag_parameters["config_file"]
        LOGGER.debug('Command-line Parameters: %s', dag_parameters)

        dag_parameters.update(self._get_dag_task_parameters_from_file(dag, "DAG", config_file_path))

        if "task" not in dag_parameters:
            dag_parameters["task"] = "DAG"

        LOGGER.debug('DAG Parameters: %s', dag_parameters)

        return dag_parameters

    def _get_dag_task_parameters(self, dag_parameters):
        dag_id = dag_parameters["dag"].upper()
        dag, _ = self._parse_dag_id(dag_id)
        task = dag_parameters.get("task", "DAG").upper()
        execution_time = dag_parameters["execution_time"].upper()
        config_file_path = dag_parameters["config_file"]

        dag_task_parameters = self._get_dag_task_parameters_from_file(dag, task, config_file_path)
        LOGGER.debug('Raw DAG Task Parameters: %s', dag_task_parameters)

        if task == 'DAG':
            state = self._get_state_plugin(dag_task_parameters)

            dag_task_parameters["task_statuses"] = state.get_all_statuses(dag, execution_time)

        return dag_task_parameters

    @classmethod
    def _resolve_dynamic_parameters(cls, task_parameters):
        dynamic_parameters = task_parameters.get("parameters", {})
        LOGGER.debug('Dynamic DAG Task Parameters: %s', dynamic_parameters)

        dynamic_loader = ReferenceEnvironmentLoader(dynamic_parameters)
        dynamic_loader.load(environment=task_parameters)

        return task_parameters

    def _start_dag_run(self):
        dag = self._get_dag_id()
        task = self._get_task_id()
        execution_time = self._get_execution_time()
        state = self._get_state_plugin(self._task_parameters)

        success = state.set_task_status(dag, task, execution_time, Status.RUNNING)

        if not success:
            LOGGER.error('Unable to set status of task %s of dag %s to Running', task, dag)
