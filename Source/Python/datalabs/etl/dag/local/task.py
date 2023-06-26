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
def run_dag_processor(dag, execution_time, parameters):
    runtime_parameters = dict(
        dag=dag,
        execution_time=execution_time,
        parameters=parameters
    )

    os.environ['TASK_RESOLVER_CLASS'] = "datalabs.task.EnvironmentTaskResolver"
    os.environ['TASK_CLASS'] = "datalabs.etl.dag.process.task.DAGProcessorTask"
    task_wrapper = DAGProcessorTaskWrapper(runtime_parameters)

    return task_wrapper.run()


# @app.task
def run_task_processor(dag, task, execution_time, parameters):
    runtime_parameters = dict(
        dag=dag,
        task=task,
        execution_time=execution_time,
        parameters=parameters
    )

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
        dag_id = self._parameters["dag"].upper()
        dag, _ = self._parse_dag_id(dag_id)
        config_file_path = self._parameters["parameters"]["config_file"]
        dynamic_parameters = dict(config_file=config_file_path)
        task_parameters = dict(
            dag=dag,
            execution_time=self._parameters["execution_time"]
        )

        task_parameters.update(self._get_dag_task_parameters_from_file(dag, "DAG", config_file_path))

        task_parameters["parameters"] = dynamic_parameters

        if "parameters" in self._parameters:
            dynamic_parameters.update(self._parameters["parameters"])

        return task_parameters

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

    @classmethod
    def _parse_dag_id(cls, dag):
        base_name = dag
        iteration = None
        components = dag.split(':')

        if len(components) == 2:
            base_name, iteration = components

        return base_name, iteration


class TaskProcessorTaskWrapper(DAGProcessorTaskWrapper):
    def _get_task_parameters(self):
        ''' Get parameters the Task Processor. '''
        dag_parameters = super()._get_task_parameters()
        dag_id = self._parameters["dag"].upper()
        dag, _ = self._parse_dag_id(dag_id)
        task = self._parameters["task"].upper()
        config_file_path = dag_parameters["parameters"]["config_file"]

        task_parameters = self._get_dag_task_parameters_from_file(dag, task, config_file_path)

        task_parameters["task"] = task

        return self._merge_parameters(dag_parameters, task_parameters)
