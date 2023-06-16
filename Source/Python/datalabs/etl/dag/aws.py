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


class DAGTaskWrapper(DynamoDBTaskParameterGetterMixin, datalabs.etl.dag.task.DAGTaskWrapper):
    def _get_runtime_parameters(self, parameters):
        command_line_parameters = json.loads(parameters[1])
        LOGGER.debug('Command-line Parameters: %s', command_line_parameters)

        return self._supplement_runtime_parameters(command_line_parameters)

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

    def _get_task_resolver_class(self):
        task_resolver_class_name = os.environ.get('TASK_RESOLVER_CLASS', 'datalabs.etl.dag.resolve.TaskResolver')
        task_resolver_class = import_plugin(task_resolver_class_name)

        if not hasattr(task_resolver_class, 'get_task_class'):
            raise TypeError(f'Task resolver {task_resolver_class_name} has no get_task_class method.')

        return task_resolver_class

    def _get_dag_task_parameters(self):
        dag_id = self._get_dag_id()
        dag_name = self._get_dag_name()
        task = self._get_task_id()
        execution_time = self._get_execution_time()
        dag_task_parameters = self._get_dag_task_parameters_from_dynamodb(dag_name, task)
        LOGGER.debug('Raw DAG Task Parameters: %s', dag_task_parameters)
        dynamic_parameters = self._runtime_parameters.get("parameters", {})
        LOGGER.debug('Dynamic DAG Task Parameters: %s', dynamic_parameters)

        if task == 'DAG':
            state = self._get_state_plugin(self._parameters)
            dag_task_parameters["task_statuses"] = state.get_all_statuses(dag_id, execution_time)
        else:
            self._override_runtime_parameters(dag_task_parameters)

            dag_task_parameters = self._remove_bootstrap_parameters(dag_task_parameters)
        LOGGER.debug('Pre-dynamic resolution DAG Task Parameters: %s', dag_task_parameters)

        dynamic_loader = ReferenceEnvironmentLoader(dynamic_parameters)
        dynamic_loader.load(environment=dag_task_parameters)

        LOGGER.debug('Final DAG Task Parameters: %s', dag_task_parameters)

        return dag_task_parameters

    def _supplement_runtime_parameters(self, runtime_parameters):
        dag_id = runtime_parameters["dag"].upper()
        dag_name, _ = self._parse_dag_id(dag_id)
        dag_parameters = self._get_dag_parameters(dag_name)
        LOGGER.debug('DAG Parameters: %s', dag_parameters)

        runtime_parameters.update(dag_parameters)

        if "task" not in runtime_parameters:
            runtime_parameters["task"] = "DAG"

        LOGGER.debug('Runtime Parameters: %s', runtime_parameters)

        return runtime_parameters

    def _override_runtime_parameters(self, task_parameters):
        overrides = json.loads(task_parameters.pop("OVERRIDES", "{}"))

        self._runtime_parameters.update({k:v for k, v in overrides.items() if k in self._runtime_parameters})

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

    def _notify_dag(self):
        dag_topic = self._runtime_parameters["DAG_TOPIC_ARN"]
        dynamic_parameters = self._runtime_parameters.get("parameters")
        notifier = SNSDAGNotifier(dag_topic)

        notifier.notify(self._get_dag_id(), self._get_execution_time(), dynamic_parameters)

    def _notify_task(self, task):
        task_topic = self._runtime_parameters["TASK_TOPIC_ARN"]
        dynamic_parameters = self._runtime_parameters.get("parameters")
        notifier = SNSTaskNotifier(task_topic)

        notifier.notify(self._get_dag_id(), task, self._get_execution_time(), dynamic_parameters)
