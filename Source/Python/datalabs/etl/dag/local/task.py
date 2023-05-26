'''Celery task creation'''
import os
import logging

from   celery import Celery  # pylint: disable=import-error

from   datalabs.etl.task import ExecutionTimeMixin
import datalabs.etl.dag.task
from   datalabs.access.parameter.file import FileEnvironmentLoader

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

class FileTaskParameterGetterMixin:
    # pylint: disable=redefined-outer-name
    @classmethod
    def _get_dag_task_parameters_from_file(cls, dag: str, task: str, config_file):
        file_loader = FileEnvironmentLoader(dict(
            dag=dag,
            task=task,
            path=config_file
        ))
        parameters = file_loader.load()

        return parameters

class DAGProcessorTaskWrapper(
    ExecutionTimeMixin,
    FileTaskParameterGetterMixin,
    datalabs.etl.dag.task.DAGTaskWrapper
):
    def _get_runtime_parameters(self, parameters):
        LOGGER.debug('Event: %s', parameters)
        return parameters

    def _get_dag_task_parameters(self):
        ''' Get parameters for the DAG Processor. '''
        dag = self._get_dag_id()
        dag_name = self._get_dag_name()
        config_file_path = self._parameters["config_file"]
        dag_parameters = dict(dag=dag, execution_time=self._get_execution_time())
        dynamic_parameters = dict(config_file=config_file_path)

        dag_parameters.update(self._get_dag_task_parameters_from_file(dag_name, "LOCAL", config_file_path))

        if "parameters" in self._runtime_parameters:
            dynamic_parameters.update(self._runtime_parameters["parameters"])

        dag_parameters["parameters"] = dynamic_parameters

        return dag_parameters


class TaskProcessorTaskWrapper(
    ExecutionTimeMixin,
    FileTaskParameterGetterMixin,
    datalabs.etl.dag.task.DAGTaskWrapper
):
    def _get_runtime_parameters(self, parameters):
        LOGGER.debug('Event: %s', parameters)
        return parameters

    def _get_dag_task_parameters(self):
        ''' Get parameters the Task Processor. '''
        dag = self._get_dag_id()
        dag_name = self._get_dag_name()
        task = self._get_task_id()
        config_file_path = self._parameters["parameters"]["config_file"]
        dag_parameters = dict(dag=dag, task=task, execution_time=self._get_execution_time())
        dynamic_parameters = dict(config_file=config_file_path)

        dag_parameters.update(self._get_dag_task_parameters_from_file(dag_name, "LOCAL", config_file_path))

        task_parameters = self._get_dag_task_parameters_from_file(dag_name, task, config_file_path)

        dag_parameters = self._override_dag_parameters(dag_parameters, task_parameters)

        dag_parameters = self._add_dynamic_dag_parameters(dag_parameters, self._runtime_parameters["parameters"])

        return dag_parameters

    @classmethod
    def _override_dag_parameters(cls, dag_parameters, task_parameters):
        dag_parameters.update({key:value for key, value in task_parameters.items() if key in dag_parameters})

        return dag_parameters

    def _add_dynamic_dag_parameters(self, dag_parameters, dynamic_parameters):
        if "parameters" in self._runtime_parameters:
            dynamic_parameters.update(self._runtime_parameters["parameters"])

            dag_parameters["parameters"] = dynamic_parameters

        return dag_parameters
