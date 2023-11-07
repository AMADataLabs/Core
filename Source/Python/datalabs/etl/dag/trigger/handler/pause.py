""" DAG Scheduler trigger handler. """
from   datalabs.etl.dag.notify.sns import SNSDAGNotifier
from   datalabs.etl.dag.trigger.handler import task

class TriggerHandlerTask(task.TriggerHandlerTask):
    def _get_dag_parameters(self, event: dict) -> dict:
        '''
        1. Get paused DAG DynamoDB table entries
        2. For each, set the dynamic parameters to be the execution time ("execution_time") from the associated entry
        3. Return a dict with dag_id=dynamic_parameters for each table entry
        '''
        paused_dags = dict(
            MARKETING_AGGREGATOR={"execution_time": ...},
            PAUSED_DAG={"execution_time": ...},
        )

        return paused_dags

    def _notify_dag_processor(self, notifier: SNSDAGNotifier, dag: str, dynamic_parameters: dict):
        execution_time = self._parameters.pop["execution_time"]

        notifier.notify(dag, execution_time, dynamic_parameters)
