""" Task wrapper for DAGs and DAG tasks running in AWS. """
import json
import logging
import os

from   datalabs.access.parameter.dynamodb import DynamoDBTaskParameterGetterMixin
from   datalabs.access.parameter.system import ReferenceEnvironmentLoader
from   datalabs.etl.dag.notify.sns import SNSDAGNotifier
from   datalabs.etl.dag.notify.sns import SNSTaskNotifier
from   datalabs.etl.dag.state import Status
from   datalabs.plugin import import_plugin
import datalabs.etl.dag.task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class SNSProcessorNotifierMixin:
    def _notify_dag(self):
        dynamic_parameters = dict(
            config_file=self._task_parameters["config_file"]
        )

        if "parameters" in self._task_parameters:
            dynamic_parameters.update(self.runtime_parameters["parameters"])

        SNSDAGNotifier.notify(self._get_dag_id(), self._get_execution_time(), dynamic_parameters)

    def _notify_task(self, task):
        dynamic_parameters = dict(
            config_file=self._task_parameters["config_file"]
        )

        if "parameters" in self._task_parameters:
            dynamic_parameters.update(self._task_parameters["parameters"])

        SNSTaskNotifier.notify(self._get_dag_id(), task, self._get_execution_time(), dynamic_parameters)


class DAGTaskWrapper(DynamoDBTaskParameterGetterMixin, SNSProcessorNotifierMixin, datalabs.etl.dag.task.DAGTaskWrapper):
    def _pre_run(self):
        super()._pre_run()
        LOGGER.debug('Pre-dynamic resolution DAG Task Parameters: %s', self._task_parameters)

        self._task_parameters = self._resolve_dynamic_parameters(self._task_parameters)

        LOGGER.debug('Final DAG Task Parameters: %s', self._task_parameters)

        if self._get_task_id() == 'DAG':
            self._start_dag_run()

    def _get_task_resolver_class(self):
        task_resolver_class_name = os.environ.get('TASK_RESOLVER_CLASS', 'datalabs.etl.dag.resolve.TaskResolver')
        task_resolver_class = import_plugin(task_resolver_class_name)

        if not hasattr(task_resolver_class, 'get_task_class'):
            raise TypeError(f'Task resolver {task_resolver_class_name} has no get_task_class method.')

        return task_resolver_class

    def _get_dag_parameters(self):
        dag_parameters = json.loads(self._parameters[1])
        dag_id = dag_parameters["dag"].upper()
        dag, _ = self._parse_dag_id(dag_id)
        LOGGER.debug('Command-line Parameters: %s', dag_parameters)

        dag_parameters.update(self._get_dag_task_parameters_from_dynamodb(dag, "DAG"))

        if "task" not in dag_parameters:
            dag_parameters["task"] = "DAG"

        LOGGER.debug('DAG Parameters: %s', dag_parameters)

        return dag_parameters

    def _get_dag_task_parameters(self, dag_parameters):
        dag_id = dag_parameters["dag"].upper()
        dag, _ = self._parse_dag_id(dag_id)
        task = dag_parameters.get("task", "DAG").upper()
        execution_time = dag_parameters["execution_time"].upper()

        dag_task_parameters = self._get_dag_task_parameters_from_dynamodb(dag, task)
        LOGGER.debug('Raw DAG Task Parameters: %s', dag_task_parameters)

        if task == 'DAG':
            state = self._get_state_plugin(self._task_parameters)

            self._task_parameters["task_statuses"] = state.get_all_statuses(dag, execution_time)

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
