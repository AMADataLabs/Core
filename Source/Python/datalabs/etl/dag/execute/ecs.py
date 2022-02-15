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
class FargateDAGExecutorParameters:
    dag: str
    job_queue: str
    job_definition: str
    execution_time: str
    unknowns: dict = None


class FargateDAGExecutorTask(Task):
    PARAMETER_CLASS = FargateDAGExecutorParameters

    def run(self):
        with AWSClient("batch") as awslambda:
            container_overrides = dict(
                command=["python", "task.py", str({'dag': self._parameters.dag,
                                                   'type': 'DAG',
                                                   'execution_time': self._parameters.execution_time})
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
class FargateTaskExecutorParameters:
    dag: str
    job_queue: str
    job_definition: str
    execution_time: str
    task: str
    unknowns: dict = None


class FargateTaskExecutorTask(Task):
    PARAMETER_CLASS = FargateTaskExecutorParameters

    def run(self):
        with AWSClient("batch") as awslambda:
            container_overrides = dict(
                command=["python", "task.py", str({'dag': self._parameters.dag,
                                                   'type': 'Task',
                                                   'task': self._parameters.task,
                                                   'execution_time': self._parameters.execution_time})
                         ]
            )

            awslambda.submit_job(
                jobName=self._parameters.dag,
                jobQueue=self._parameters.job_queue,
                jobDefinition=self._parameters.job_definition,
                containerOverrides=container_overrides
            )
