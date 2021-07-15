''' Classes for executing DAGs and DAG tasks locally '''
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
class LambdaDAGExecutorParameters:
    dag: str
    function: str
    execution_time: str
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

            awslambda.invoke(
                FunctionName=self._parameters.function,
                InvocationType='Event',
                Payload=payload
            )
