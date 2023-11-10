""" DAG Scheduler trigger handler. """
from   datalabs.access.aws import AWSClient
from   datalabs.access.cpt.api.snomed import MapSearchEndpointTask
from   datalabs.etl.dag.notify.sns import SNSDAGNotifier
from   datalabs.etl.dag.trigger.handler import task
from   datalabs.etl.dag.state.dynamodb import DynamoDBClientMixin


# pylint: disable=protected-access
class TriggerHandlerTask(task.TriggerHandlerTask, DynamoDBClientMixin):
    def _get_dag_parameters(self, trigger_parameters: dict, event: dict) -> list:
        '''
        1. Get paused DAG DynamoDB table entries
        2. For each, set the dynamic parameters to be the execution time ("execution_time") from the associated entry
        3. Return a dict with dag_id=dynamic_parameters for each table entry

        DynamoDB Table
        dag_id                  execution_time          ttl
        MARKETING_AGGREGATOR    2023-10-05T00:00:00     123456
        SOME_OTHER_DAG          2023-11-05T00:00:00     123456
        YET_ANOTHER_DAG         2023-10-20T00:00:00     123456
        '''
        paused_dags = []

        with AWSClient("dynamodb", **self._connection_parameters()) as dynamodb:
            results = MapSearchEndpointTask._paginate(
                dynamodb,
                f"SELECT dag_id, execution_time FROM \"{self._parameters.table}\""
            )

            paused_dags = [(x["dag_id"]["S"], dict(execution_time=x["execution_time"]["S"])) for x in results]

        return paused_dags

    def _notify_dag_processor(self, notifier: SNSDAGNotifier, dag: str, dynamic_parameters: dict):
        execution_time = self._parameters.pop["execution_time"]

        notifier.notify(dag, execution_time, dynamic_parameters)
