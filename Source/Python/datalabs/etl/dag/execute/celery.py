''' Classes for executing DAGs via AWS Batch'''
from   dataclasses import dataclass
import json
import logging
import os
import subprocess

from   datalabs.access.aws import AWSClient
from   datalabs.parameter import add_schema
from   datalabs.task import Task
from   datalabs.plugin import import_plugin
from   datalabs.etl.dag.celery import DAGTaskWrapper

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


@add_schema(unknowns=True)
@dataclass
class CeleryDAGExecutorParameters:
    dag: str
    execution_time: str
    parameters: dict
    unknowns: dict = None


class CeleryDAGExecutorTask(Task):
    PARAMETER_CLASS = CeleryDAGExecutorParameters

    def run(self):
        parameters = dict(
            dag=self._parameters.dag,
            type="DAG",
            execution_time=self._parameters.execution_time,
            config_file=self._parameters.parameters.pop("config_file")
        )
        
        if self._parameters.parameters:
            parameters["parameters"] = self._parameters.parameters

        LOGGER.debug('Final batch DAG parameters: %s', parameters)
        task_wrapper = DAGTaskWrapper(parameters)

        os.environ["TASK_RESOLVER_CLASS"] = "datalabs.etl.dag.resolve.TaskResolver"
    
        task_wrapper.run()


@add_schema(unknowns=True)
@dataclass
class CeleryPythonTaskExecutorParameters:
    dag: str
    execution_time: str
    task: str
    parameters: dict=None
    unknowns: dict = None


class CeleryPythonTaskExecutorTask(Task):
    PARAMETER_CLASS = CeleryPythonTaskExecutorParameters

    def run(self):
        parameters = dict(
            dag=self._parameters.dag,
            type="Task",
            task=self._parameters.task,
            execution_time=self._parameters.execution_time,
            config_file=self._parameters.parameters.pop("config_file")
        )
        
        if self._parameters.parameters:
            parameters["parameters"] = self._parameters.parameters

        LOGGER.debug('Final batch DAG parameters: %s', parameters)

        task_wrapper = DAGTaskWrapper(parameters)

        os.environ["TASK_RESOLVER_CLASS"] = "datalabs.etl.dag.resolve.TaskResolver"
    
        task_wrapper.run()




@add_schema(unknowns=True)
@dataclass
class BatchJavaTaskExecutorParameters:
    dag: str
    execution_time: str
    task: str
    job_queue: str
    job_definition: str
    unknowns: dict = None


class BatchJavaTaskExecutorTask(Task):
    PARAMETER_CLASS = BatchJavaTaskExecutorParameters

    def run(self):
        execution_time = self._parameters.execution_time.replace(" ", "T")
        job_name = f"{self._parameters.dag.replace(':', '')}__{self._parameters.task}"\
                   f"__{execution_time.replace(':', '').replace('.', '')}"

        LOGGER.info('Submitting job %s to queue %s.', job_name, self._parameters.job_queue)
        command = [
            "java",
            "datalabs.tool.TaskRunner",
            "--arg",
            "java",
            "--arg",
            f"{self._parameters.dag}__{self._parameters.task}__{execution_time}"
        ]
        subprocess.run(command)

