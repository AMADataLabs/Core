''' Classes for executing DAGs and DAG tasks locally '''
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
class LambdaDAGExecutorParameters:
    dag: str
    lambda_function: str
    execution_time: str
    parameters: str=None
    unknowns: dict=None


class LambdaDAGExecutorTask(Task):
    PARAMETER_CLASS = LambdaDAGExecutorParameters

    def run(self):
        with AWSClient("lambda") as awslambda:
            payload = dict(
                dag=self._parameters.dag,
                type="DAG",
                execution_time=self._parameters.execution_time
            )

            if self._parameters.parameters:
                payload["parameters"] = json.loads(self._parameters.parameters)

            awslambda.invoke(
                FunctionName=self._parameters.lambda_function,
                InvocationType='Event',
                Payload=json.dumps(payload)
            )


@add_schema(unknowns=True)
@dataclass
class LambdaTaskExecutorParameters:
    dag: str
    task: str
    lambda_function: str
    execution_time: str
    parameters: str=None
    unknowns: dict=None


class LambdaTaskExecutorTask(Task):
    PARAMETER_CLASS = LambdaTaskExecutorParameters

    def run(self):
        with AWSClient("lambda") as awslambda:
            payload = dict(
                dag=self._parameters.dag,
                type="Task",
                task=self._parameters.task,
                execution_time=self._parameters.execution_time
            )

            if self._parameters.parameters:
                payload["parameters"] = json.loads(self._parameters.parameters)

            LOGGER.debug('TaskProcessor event payload: %s', payload)

            awslambda.invoke(
                FunctionName=self._parameters.lambda_function,
                InvocationType='Event',
                Payload=json.dumps(payload)
            )
