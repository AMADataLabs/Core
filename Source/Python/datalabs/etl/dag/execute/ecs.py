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
    job: str
    execution_time: str
    unknowns: dict = None


class FargateDAGExecutorTask(Task):
    PARAMETER_CLASS = FargateDAGExecutorParameters

    def run(self):
        with AWSClient("batch") as awslambda:
            container_overrides = dict(
                command=["python", "task.py",
                         {
                             'dag': self._parameters.dag,
                             'type': 'DAG',
                             'execution_time': self._parameters.execution_time
                         }
                         ]
            )

            awslambda.submit_job(
                jobName=self._parameters.dag,
                jobQueue='{}-job-definition'.format(self._job),
                jobDefinition='{}-job-queue'.format(self._job),
                containerOverrides=container_overrides
            )


@add_schema(unknowns=True)
@dataclass
class FargateTaskExecutorParameters:
    dag: str
    task: str
    job: str
    execution_time: str
    unknowns: dict = None


class FargateTaskExecutorTask(Task):
    PARAMETER_CLASS = FargateDAGExecutorParameters

    def run(self):
        with AWSClient("batch") as awslambda:
            container_overrides = dict(
                command=["python", "task.py",
                         {
                             'dag': self._parameters.dag,
                             'type': 'Task',
                             'task': self._parameters.task,
                             'execution_time': self._parameters.execution_time
                         }
                         ]
            )

            awslambda.submit_job(
                jobName=self._parameters.dag,
                jobQueue='{}-job-definition'.format(self._parameters.job),
                jobDefinition='{}-job-queue'.format(self._parameters.job),
                containerOverrides=container_overrides
            )
