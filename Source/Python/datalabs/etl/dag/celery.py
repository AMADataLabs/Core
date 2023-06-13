""" Task wrapper for a Celery runtime environment. """
import logging

from   datalabs.access.parameter.file import FileEnvironmentLoader
from   datalabs.access.parameter.system import ReferenceEnvironmentLoader
from   datalabs.etl.dag.notify.celery import CeleryDAGNotifier, CeleryTaskNotifier
from   datalabs.parameter import ParameterValidatorMixin
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
    def _notify_dag(self):
        dynamic_parameters = dict(
            config_file=self._runtime_parameters["config_file"]
        )

        if "parameters" in self._runtime_parameters:
            dynamic_parameters.update(self.runtime_parameters["parameters"])

        CeleryDAGNotifier.notify(self._get_dag_id(), self._get_execution_time(), dynamic_parameters)

    def _notify_task(self, task):
        dynamic_parameters = dict(
            config_file=self._runtime_parameters["config_file"]
        )

        if "parameters" in self._runtime_parameters:
            dynamic_parameters.update(self._runtime_parameters["parameters"])

        CeleryTaskNotifier.notify(self._get_dag_id(), task, self._get_execution_time(), dynamic_parameters)


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

        if task != "DAG":
            state = self._get_state_plugin(self._parameters)

            success = state.set_task_status(dag, task, execution_time, Status.RUNNING)

            if not success:
                LOGGER.error('Unable to set status of task %s of dag %s to Running', task, dag)

    def _get_dag_task_parameters(self):
        dag_id = self._get_dag_id()
        dag_name = self._get_dag_name()
        task = self._get_task_id()
        execution_time = self._get_execution_time()
        config_file_path = self._parameters["config_file"]
        dynamic_parameters = self._runtime_parameters.get("parameters", {})
        LOGGER.debug('Dynamic DAG Task Parameters: %s', dynamic_parameters)

        dag_task_parameters = self._get_dag_task_parameters_from_file(dag_name, task, config_file_path)
        LOGGER.debug('Raw DAG Task Parameters: %s', dag_task_parameters)

        if task == 'DAG':
            state = self._get_state_plugin(self._parameters)
            dag_task_parameters["task_statuses"] = state.get_all_statuses(dag_id, execution_time)
        else:
            self._override_runtime_parameters(dag_task_parameters.pop("OVERRIDES", {}))
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

        LOGGER.debug('Runtime Parameters: %s', runtime_parameters)

        return runtime_parameters

    def _override_runtime_parameters(self, overrides):
        for name, value in list(overrides.items()):
            if name in self._runtime_parameters:
                self._runtime_parameters[name] = value

    @classmethod
    def _remove_bootstrap_parameters(cls, task_parameters):
        if 'TASK_CLASS' in task_parameters:
            task_parameters.pop("TASK_CLASS")

        return task_parameters

    def _get_dag_parameters(self, dag, path):
        LOGGER.debug('Getting DAG Parameters for %s...', dag)
        dag_parameters = self._get_dag_task_parameters_from_file(dag, "DAG", path)
        LOGGER.debug('Raw DAG Parameters: %s', dag_parameters)

        return dag_parameters
