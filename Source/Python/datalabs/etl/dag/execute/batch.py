''' Classes for executing DAGs via AWS Batch'''
from   dataclasses import dataclass
import logging

from   datalabs.access.aws import AWSClient
from   datalabs.parameter import add_schema
from   datalabs.task import Task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


@add_schema(unknowns=True)
@dataclass
class BatchDAGExecutorParameters:
    dag: str
    execution_time: str
    job_queue: str
    job_definition: str
    unknowns: dict = None


class BatchDAGExecutorTask(Task):
    PARAMETER_CLASS = BatchDAGExecutorParameters

    def run(self):
        execution_time = self._parameters.execution_time.replace(" ", "T")

        with AWSClient("batch") as awslambda:
            container_overrides = dict(
                command=[
                    "python",
                    "task.py",
                    f'{{"dag": "{self._parameters.dag}","type": "DAG", "execution_time": "{execution_time}"}}'
                ]

            )

            awslambda.submit_job(
                jobName=self._parameters.dag,
                jobQueue=self._parameters.job_queue,
                jobDefinition=self._parameters.job_definition,
                containerOverrides=container_overrides
            )


@add_schema(unknowns=True)
@dataclass
class BatchPythonTaskExecutorParameters:
    dag: str
    execution_time: str
    task: str
    job_queue: str
    job_definition: str
    unknowns: dict = None


class BatchPythonTaskExecutorTask(Task):
    PARAMETER_CLASS = BatchPythonTaskExecutorParameters

    def run(self):
        execution_time = self._parameters.execution_time.replace(" ", "T")

        with AWSClient("batch") as batch:
            container_overrides = dict(
                command=[
                    "python",
                    "task.py",
                    f"{self._parameters.dag}__{self._parameters.task}__{execution_time}"
                ]
            )

            batch.submit_job(
                jobName=f"{self._parameters.dag}__{self._parameters.task}__{execution_time}",
                jobQueue=self._parameters.job_queue,
                jobDefinition=self._parameters.job_definition,
                containerOverrides=container_overrides
            )


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

        with AWSClient("batch") as batch:
            container_overrides = dict(
                command=[
                    "java",
                    "datalabs.tool.TaskRunner",
                    "--arg",
                    "java",
                    "--arg",
                    f"{self._parameters.dag}__{self._parameters.task}__{execution_time}"
                ]
            )

            batch.submit_job(
                jobName=f"{self._parameters.dag}__{self._parameters.task}__{execution_time}",
                jobQueue=self._parameters.job_queue,
                jobDefinition=self._parameters.job_definition,
                containerOverrides=container_overrides
            )
