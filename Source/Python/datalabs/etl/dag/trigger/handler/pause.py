""" DAG Scheduler trigger handler. """
from   datalabs.access.aws import AWSClient
from   datalabs.access.cpt.api.snomed import MapSearchEndpointTask
from   datalabs.etl.dag.notify.sns import SNSDAGNotifier
from   datalabs.etl.dag.trigger.handler import task

# pylint: disable=no-member, protected-access
class TriggerHandlerTask(task.TriggerHandlerTask):
    def _get_dag_parameters(self, trigger_parameters: dict, event: dict) -> dict:
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
        paused_dags = {}
        current_rows = []

        # Paused DAG table: trigger_parameters["PAUSED_DAG_TABLE"]
        #
        # 1a. Setup AWSClient for DynamoDB using paused DAG table
        # 1b. Iterate through entries in paused DAG table
        #  2. Append paused_dags[item["dag_id"]] = dict(execution_time=item["execution_time"])
        #
        # paushed dags should look like this after step #2:
        # dict(
        #     MARKETING_AGGREGATOR={"execution_time": "2023-10-05T00:00:00"},
        #     SOME_OTHER_DAG={"execution_time": "2023-11-05T00:00:00"},
        #     YET_ANOTHER_DAG={"execution_time": "2023-10-20T00:00:00"}
        # )

        with AWSClient("dynamodb", **self._connection_parameters()) as dynamodb:
            results = MapSearchEndpointTask._paginate(
                dynamodb,
                f"SELECT dag_id, execution_time FROM \"{self._parameters.table}\""
            )

            current_rows = [(x["dag_id"]["S"], x["execution_time"]["S"]) for x in results]

            for dag_id, execution_time in current_rows:
                if dag_id in paused_dags:
                    paused_dags[dag_id]["execution_time"] = [paused_dags[dag_id]["execution_time"]] + [execution_time]
                else:
                    paused_dags[dag_id]=(dict(execution_time=execution_time))

        return paused_dags

    def _notify_dag_processor(self, notifier: SNSDAGNotifier, dag: str, dynamic_parameters: dict):
        execution_time = self._parameters.pop["execution_time"]

        notifier.notify(dag, execution_time, dynamic_parameters)
