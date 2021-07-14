''' AWS Lambda DAG plugin executor implementation. '''
from   enum import Enum
import logging

from   datalabs.access.aws import AWSClient
from   datalabs.etl.dag.plugin.base import DAGPluginExecutor

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class PluginEventTypes(Enum):
    DAG='DAG'
    TASK='Task'


class LambdaDAGPluginExecutor(DAGPluginExecutor):
    def __init__(self, parameters: dict):
        self._function = parameters["function"]

    def run_dag(self, execution_time, dag):
        self._invoke_lambda(PluginEventTypes.DAG, execution_time)

    def run_task(self, execution_time, dag, task):
        self._invoke_lambda(PluginEventTypes.TASK, execution_time, task)

    # pylint: disable=redefined-builtin
    def _invoke_lambda(self, type: PluginEventTypes, execution_time, task=None):
        with AWSClient("lambda") as awslambda:
            payload = dict(
                type=type.value,
                execution_time=execution_time
            )

            if type == PluginEventTypes.TASK:
                payload["task"] = task

            response = awslambda.invoke(
                FunctionName=self._function,
                InvocationType='RequestResponse',
                Payload=payload
            )

            LOGGER.debug('DAG Plugin Response: %s', response)
