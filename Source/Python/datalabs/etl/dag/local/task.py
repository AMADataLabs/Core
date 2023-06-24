'''Celery task creation'''
import os
import logging

from   datalabs.etl.task import ExecutionTimeMixin, TaskWrapper
from   datalabs.access.parameter.file import FileTaskParameterGetterMixin
from   datalabs.etl.dag.task import DAGTaskIDMixin

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# app = Celery('task', broker='amqp://', backend='rpc://')


# @app.task
def run_dag_processor(dag, execution_time, config_file, parameters=None):
    runtime_parameters = dict(
        dag=dag,
        execution_time=execution_time,
        config_file=config_file
    )
    if parameters is not None:
        runtime_parameters['parameters'] = parameters

    os.environ['TASK_RESOLVER_CLASS'] = "datalabs.task.EnvironmentTaskResolver"
    os.environ['TASK_CLASS'] = "datalabs.etl.dag.process.task.DAGProcessorTask"
    task_wrapper = DAGProcessorTaskWrapper(runtime_parameters)

    return task_wrapper.run()


# @app.task
def run_task_processor(dag, task, execution_time, parameters=None):
    runtime_parameters = dict(
        dag=dag,
        task=task,
        execution_time=execution_time
    )
    if parameters is not None:
        runtime_parameters['parameters'] = parameters

    os.environ['TASK_RESOLVER_CLASS'] = "datalabs.task.EnvironmentTaskResolver"
    os.environ['TASK_CLASS'] = "datalabs.etl.dag.process.task.TaskProcessorTask"
    task_wrapper = TaskProcessorTaskWrapper(runtime_parameters)

    return task_wrapper.run()


class DAGProcessorTaskWrapper(
    ExecutionTimeMixin,
    DAGTaskIDMixin,
    FileTaskParameterGetterMixin,
    TaskWrapper
):
    def _get_task_parameters(self):
        LOGGER.debug('Event: %s', self._parameters)
        return self._parameters

    def _get_task_parameters(self):
        ''' Get parameters for the DAG Processor. '''
        dag = self._get_dag_id()
        dag_name = self._get_dag_name()
        config_file_path = self._parameters["config_file"]
        dag_parameters = dict(dag=dag, execution_time=self._get_execution_time())
        dynamic_parameters = dict(config_file=config_file_path)

        dag_parameters.update(self._get_dag_task_parameters_from_file(dag_name, "DAG", config_file_path))

        if "parameters" in self._task_parameters:
            dynamic_parameters.update(self._task_parameters["parameters"])

        dag_parameters["parameters"] = dynamic_parameters

        return dag_parameters

    def _handle_success(self) -> (int, dict):
        return "Success"

    def _handle_exception(self, exception) -> (int, dict):
        LOGGER.exception('An exception occured while running the processor.')

        return f'Failed: {str(exception)}'

    def _get_dag_id(self):
        return self._task_parameters["dag"].upper()

    def _get_dag_name(self):
        base_name, _ = self._parse_dag_id(self._get_dag_id())

        return base_name

    def _get_execution_time(self):
        return self._task_parameters["execution_time"].upper()

    @classmethod
    def _parse_dag_id(cls, dag):
        base_name = dag
        iteration = None
        components = dag.split(':')

        if len(components) == 2:
            base_name, iteration = components

        return base_name, iteration


class TaskProcessorTaskWrapper(
    ExecutionTimeMixin,
    DAGTaskIDMixin,
    FileTaskParameterGetterMixin,
    TaskWrapper
):
    def _get_task_parameters(self):
        LOGGER.debug('Event: %s', self._parameters)
        return self._parameters

    def _get_task_parameters(self):
        ''' Get parameters the Task Processor. '''
        dag = self._get_dag_id()
        dag_name = self._get_dag_name()
        task = self._get_task_id()
        config_file_path = self._parameters["parameters"]["config_file"]
        dag_parameters = dict(dag=dag, task=task, execution_time=self._get_execution_time())
        dynamic_parameters = self._task_parameters.get("parameters") or {}

        dynamic_parameters.update(dict(config_file=config_file_path))

        dag_parameters.update(self._get_dag_task_parameters_from_file(dag_name, "DAG", config_file_path))

        task_parameters = self._get_dag_task_parameters_from_file(dag_name, task, config_file_path)

        dag_parameters = self._override_dag_parameters(dag_parameters, task_parameters)

        dag_parameters = self._add_dynamic_dag_parameters(dag_parameters, self._task_parameters["parameters"])

        return dag_parameters

    def _handle_success(self) -> (int, dict):
        return "Success"

    def _handle_exception(self, exception) -> (int, dict):
        LOGGER.exception('An exception occured while running the processor.')

        return f'Failed: {str(exception)}'

    @classmethod
    def _override_dag_parameters(cls, dag_parameters, task_parameters):
        dag_parameters.update({key:value for key, value in task_parameters.items() if key in dag_parameters})

        return dag_parameters

    def _add_dynamic_dag_parameters(self, dag_parameters, dynamic_parameters):
        if "parameters" in self._task_parameters:
            dynamic_parameters.update(self._task_parameters["parameters"])

            dag_parameters["parameters"] = dynamic_parameters

        return dag_parameters
