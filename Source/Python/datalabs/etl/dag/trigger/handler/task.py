from   abc import ABCMeta, ABC, abstractmethod

from   datalabs.etl.dag.notify.sns import SNSDAGNotifier
from   datalabs.task import Task


@add_schema(unknowns=True)
@dataclass
class TriggerHandlerParameters:
    dag_topi_arn: str
    event: dict
    unknowns: dict=None


class TriggerHandlerTask(Task, ABC):
    def run(self) -> "list<bytes>":
        notifier = SNSDAGNotifier(self._parameters["dag_topic_arn"])

        dag_parameters = self._get_dag_parameters(self._parameters.event)

        for dag, dynamic_parameters in dag_parameters.items():
            self._notify_dag_processor(notifier, dag, dynamic_parameters)

        return []

    @abstractmethod
    def _get_dag_parameters(self, event: dict) -> dict:
        pass

    def _notify_dag_processor(self, notifier: SNSDAGNotifier, dag: str, dynamic_parameters: dict):
        execution_time = self._parameters.event["execution_time"]

        notifier.notify(self._get_dag_id(), execution_time, dynamic_parameters)
