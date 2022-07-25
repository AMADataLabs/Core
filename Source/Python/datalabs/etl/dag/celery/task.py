'''Celery task creation'''

import os
import logging
from   celery import Celery
import datalabs.etl.dag.aws as aws
from   datalabs.etl.task import ExecutionTimeMixin
import datalabs.etl.dag.task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


app = Celery('tasks', broker='amqp://localhost')


@app.task
def run_dag_processor(dag, execution_time, parameters=None):
    runtime_parameters = dict(
        dag=dag,
        execution_time=execution_time
    )
    if parameters is not None:
        runtime_parameters['parameters'] = parameters

    os.environ['TASK_CLASS'] = "datalabs.etl.dag.process.DAGProcessorTask"
    task_wrapper = DAGProcessorTaskWrapper(runtime_parameters)

    return task_wrapper.run()


@app.task
def run_task_processor(dag, task, execution_time, parameters=None):
    runtime_parameters = dict(
        dag=dag,
        task=task,
        execution_time=execution_time
    )
    if parameters is not None:
        runtime_parameters['parameters'] = parameters

    os.environ['TASK_CLASS'] = "datalabs.etl.dag.process.TaskProcessorTask"
    task_wrapper = TaskProcessorTaskWrapper(runtime_parameters)

    return task_wrapper.run()

class DAGProcessorTaskWrapper(
    ExecutionTimeMixin,
    aws.DynamoDBTaskParameterGetterMixin,
    datalabs.etl.dag.task.DAGTaskWrapper
):
    def _get_runtime_parameters(self, parameters):
        LOGGER.debug('Event: %s', parameters)
        return parameters

    def _get_dag_task_parameters(self):
        ''' Get parameters for the DAG Processor. '''
        dag = self._get_dag_id()
        dag_name = self._get_dag_name()
        dag_parameters = dict(
            dag=dag,
            execution_time=self._get_execution_time(),
        )

        dag_parameters.update(self._get_dag_task_parameters_from_dynamodb(dag_name, "LOCAL"))

        if "parameters" in self._runtime_parameters:
            dag_parameters["parameters"] = self._runtime_parameters["parameters"]

        return dag_parameters


class TaskProcessorTaskWrapper(
    ExecutionTimeMixin,
    aws.DynamoDBTaskParameterGetterMixin,
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
        dag_parameters = dict(
            dag=dag,
            execution_time=self._get_execution_time(),
        )

        dag_parameters.update(self._get_dag_task_parameters_from_dynamodb(dag_name, "LOCAL"))
        task_parameters = self._get_dag_task_parameters_from_dynamodb(dag_name, task)
        dag_parameters = self._override_dag_parameters(dag_parameters, task_parameters)

        if "parameters" in self._runtime_parameters:
            dag_parameters["parameters"] = self._runtime_parameters["parameters"]

        dag_parameters["task"] = task

        return dag_parameters

    @classmethod
    def _override_dag_parameters(cls, dag_parameters, task_parameters):
        for key, _ in task_parameters.items():
            if key in dag_parameters:
                dag_parameters[key] = task_parameters[key]

        return dag_parameters
