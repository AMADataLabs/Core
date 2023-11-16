""" DAG Scheduler trigger handler. """
from   datalabs.access.aws import AWSClient
from   datalabs.etl.dag.notify.sns import SNSDAGNotifier
from   datalabs.etl.dag.trigger.handler import task
from   datalabs.etl.dag.state.dynamodb import DynamoDBClientMixin


class TriggerHandlerTask(task.TriggerHandlerTask, DynamoDBClientMixin):
    def _get_dag_parameters(self, trigger_parameters: dict, event: dict) -> list:
        '''
        The DynamoDB table is expected to have the following structure:

        dag_id                  execution_time          ttl
        SOME_DAG                2023-10-05T00:00:00     123456
        SOME_OTHER_DAG          2023-11-05T00:00:00     123456
        YET_ANOTHER_DAG         2023-10-20T00:00:00     123456
        '''
        paused_dags = []

        with AWSClient("dynamodb", **self._connection_parameters()) as dynamodb:
            results = self._paginate(
                dynamodb,
                f"SELECT dag_id, execution_time FROM \"{self._parameters.table}\""
            )

            paused_dags = [(x["dag_id"]["S"], dict(execution_time=x["execution_time"]["S"])) for x in results]

        return paused_dags

    @classmethod
    def _paginate(cls, dynamodb, statement):
        results = dynamodb.execute_statement(Statement=statement)

        for item in results["Items"]:
            yield item

        while "NextToken" in results:
            results = dynamodb.execute_statement(Statement=statement, NextToken=results["NextToken"])

            for item in results["Items"]:
                yield item

    def _notify_dag_processor(self, notifier: SNSDAGNotifier, dag: str, dynamic_parameters: dict):
        execution_time = self._parameters.pop["execution_time"]

        notifier.notify(dag, execution_time, dynamic_parameters)
