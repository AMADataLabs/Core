''' Classes for executing DAGs and DAG tasks locally '''
from   dataclasses import dataclass
import logging

from   datalabs.access.aws import AWSClient
from   datalabs.etl.dag.state import Status
from   datalabs.parameter import add_schema
from   datalabs.plugin import import_plugin
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


class LambdaDAGExecutor(Task):
    PARAMETER_CLASS = LambdaDAGExecutorParameters

    def run(self):
        with AWSClient("lambda") as awslambda:
            payload = dict(
                dag=self._parameters.dag,
                type="DAG",
                execution_time=execution_time
            )

            response = awslambda.invoke(
                FunctionName=self._parameters.function,
                InvocationType='Event',
                Payload=payload
            )
