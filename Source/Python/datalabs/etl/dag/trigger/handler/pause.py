""" DAG Scheduler trigger handler. """
from   datalabs.etl.dag.notify.sns import SNSDAGNotifier
from   datalabs.etl.dag.trigger.handler import task

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

        return paused_dags

    def _notify_dag_processor(self, notifier: SNSDAGNotifier, dag: str, dynamic_parameters: dict):
        execution_time = self._parameters.pop["execution_time"]

        notifier.notify(dag, execution_time, dynamic_parameters)
