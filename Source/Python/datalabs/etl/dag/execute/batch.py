''' Classes for executing DAGs via AWS Batch'''
from   dataclasses import dataclass
import json
import logging

from   datalabs.access.aws import AWSClient
from   datalabs.parameter import add_schema
from   datalabs.task import Task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@add_schema(unknowns=True)
@dataclass
class BatchDAGExecutorParameters:
    dag: str
    execution_time: str
    job_queue: str
    job_definition: str
    parameters: dict=None
    unknowns: dict = None


class BatchDAGExecutorTask(Task):
    PARAMETER_CLASS = BatchDAGExecutorParameters

    def run(self):
        job_name = f"{self._parameters.dag.replace(':', '')}__"\
                   f"{self._parameters.execution_time.replace(" ", "T").replace(':', '').replace('.', '')}"
        parameters = dict(
            dag=self._parameters.dag,
            type="DAG",
            execution_time=self._parameters.execution_time
        )

        if self._parameters.parameters:
            parameters["parameters"] = self._parameters.parameters
        LOGGER.debug('Final batch DAG parameters: %s', parameters)

        LOGGER.info('Submitting job %s to queue %s.', job_name, self._parameters.job_queue)

        with AWSClient("batch") as awslambda:
            container_overrides = dict(
                command=[
                    "python",
                    "task.py",
                    json.dumps(parameters)
                ]

            )

            awslambda.submit_job(
                jobName=job_name,
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
    parameters: dict=None
    unknowns: dict = None


class BatchPythonTaskExecutorTask(Task):
    PARAMETER_CLASS = BatchPythonTaskExecutorParameters

    def run(self):
        job_name = f"{self._parameters.dag.replace(':', '')}__{self._parameters.task}"\
                   f"__{self._parameters.execution_time.replace(" ", "T").replace(':', '').replace('.', '')}"
        parameters = dict(
            dag=self._parameters.dag,
            type="Task",
            task=self._parameters.task,
            execution_time=self._parameters.execution_time
        )

        if self._parameters.parameters:
            parameters["parameters"] = self._parameters.parameters
        LOGGER.debug('Final batch task parameters: %s', parameters)

        LOGGER.info('Submitting job %s to queue %s.', job_name, self._parameters.job_queue)

        with AWSClient("batch") as batch:
            container_overrides = dict(
                command=[
                    "python",
                    "task.py",
                    json.dumps(parameters)
                ]
            )

            batch.submit_job(
                jobName=job_name,
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
        job_name = f"{self._parameters.dag.replace(':', '')}__{self._parameters.task}"\
                   f"__{execution_time.replace(':', '').replace('.', '')}"

        LOGGER.info('Submitting job %s to queue %s.', job_name, self._parameters.job_queue)

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
                jobName=job_name,
                jobQueue=self._parameters.job_queue,
                jobDefinition=self._parameters.job_definition,
                containerOverrides=container_overrides
            )
