""" Base trigger handler task class. """
from   abc import ABC, abstractmethod
from   dataclasses import dataclass

from   datalabs.etl.dag.notify.sns import SNSDAGNotifier
from   datalabs.parameter import add_schema
from   datalabs.task import Task


@add_schema(unknowns=True)
@dataclass
class TriggerHandlerParameters:
    dag_topic_arn: str
    event: dict
    unknowns: dict=None


class TriggerHandlerTask(Task, ABC):
    PARAMETER_CLASS = TriggerHandlerParameters

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

        notifier.notify(dag, execution_time, dynamic_parameters)
