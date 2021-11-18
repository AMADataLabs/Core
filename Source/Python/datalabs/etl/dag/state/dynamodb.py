""" DynamoDB DAG state classes. """
import collections
from   dataclasses import dataclass
import logging
import time

import boto3
import botocore

from   datalabs.etl.dag.state.base import State, Status
from   datalabs.parameter import add_schema

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class DynamoDBClientMixin:
    def _connect(self):
        return boto3.client(
            'dynamodb',
            endpoint_url=self._parameters.endpoint_url,
            aws_access_key_id=self._parameters.access_key,
            aws_secret_access_key=self._parameters.secret_key,
            region_name=self._parameters.region_name
        )


class LockingStateMixin():
    TIMEOUT_SECONDS = 30

    def _lock_state(self, dynamodb, lock_id):
        locked = False
        start_time = time.time()

        while not locked and (time.time()-start_time) < self.TIMEOUT_SECONDS:
            try:
                dynamodb.put_item(
                    TableName=self._parameters.state_lock_table,
                    Item={'LockID': {'S': lock_id}, 'ttl': {'N': str(time.time()+30)}},
                    ConditionExpression="attribute_not_exists(#r)",
                    ExpressionAttributeNames={"#r": "LockID"}
                )

                locked = True
            except botocore.exceptions.ClientError as exception:
                if exception.response['Error']['Code'] != 'ConditionalCheckFailedException':
                    raise

        return locked

    def _unlock_state(self, dynamodb, lock_id):
        unlocked = False

        try:
            dynamodb.delete_item(
                TableName=self._parameters.state_lock_table,
                Key={'LockID': {'S': lock_id}},
                ConditionExpression="attribute_exists(#r)",
                ExpressionAttributeNames={"#r": "LockID"}
            )

            unlocked = True
        except botocore.exceptions.ClientError as exception:
            if exception.response['Error']['Code'] != 'ConditionalCheckFailedException':
                raise

        return unlocked


@add_schema(unknowns=True)
@dataclass
# pylint: disable=too-many-instance-attributes
class DAGStateParameters:
    state_lock_table: str
    dag_state_table: str
    endpoint_url: str=None
    access_key: str=None
    secret_key: str=None
    region_name: str=None
    unknowns: dict=None


class DAGState(DynamoDBClientMixin, LockingStateMixin, State):
    PARAMETER_CLASS = DAGStateParameters

    def get_dag_status(self, dag: str, execution_time: str):
        return self._get_status(dag, None, execution_time)

    def get_task_status(self, dag: str, task: str, execution_time: str):
        return self._get_status(dag, task, execution_time)

    def set_dag_status(self, dag: str, execution_time: str, status: Status):
        return self._set_status(dag, None, execution_time, status)

    def set_task_status(self, dag: str, task: str, execution_time: str, status: Status):
        return self._set_status(dag, task, execution_time, status)

    def get_all_statuses(self, dag: str, execution_time: str):
        dynamodb = self._connect()
        items = self._get_items_for_dag_run(dynamodb, dag, execution_time)

        return self._get_item_statuses(dynamodb, execution_time, items)

    def clear_task(self, dag: str, execution_time: str, task: str):
        dynamodb = self._connect()

        self._clear_items(dynamodb, execution_time, [dag, f"{dag}__{task}"])

    def clear_all(self, dag: str, execution_time: str):
        dynamodb = self._connect()
        items = self._get_items_for_dag_run(dynamodb, dag, execution_time)
        LOGGER.info('Deleting items for %s run of DAG %s: %s', execution_time, dag, items)

        self._clear_items(dynamodb, execution_time, items)

    def clear_upstream_tasks(self, dag_class, dag: str, execution_time: str, task: str):
        dynamodb = self._connect()
        tasks = [dag, f"{dag}__{task}"] + [f"{dag}__{task}" for task in dag_class.upstream_tasks(task)]

        self._clear_items(dynamodb, execution_time, tasks)

    def clear_downstream_tasks(self, dag_class, dag: str, execution_time: str, task: str):
        dynamodb = self._connect()
        tasks = [dag, f"{dag}__{task}"] + [f"{dag}__{task}" for task in dag_class.downstream_tasks(task)]

        self._clear_items(dynamodb, execution_time, tasks)

    def _get_status(self, dag: str, task: str, execution_time: str):
        primary_key = self._get_primary_key(dag, task)
        dynamodb = self._connect()

        return self._get_status_from_state(dynamodb, primary_key, execution_time)

    def _set_status(self, dag: str, task: str, execution_time: str, status: Status):
        primary_key = self._get_primary_key(dag, task)
        lock_id = self._get_lock_id(primary_key, execution_time)
        dynamodb = self._connect()
        succeeded = False

        locked = self._lock_state(dynamodb, lock_id)

        if locked:
            succeeded = self._set_status_if_later(dynamodb, primary_key, execution_time, status)

        self._unlock_state(dynamodb, lock_id)

        return succeeded

    def _get_items_for_dag_run(self, dynamodb, dag: str, execution_time: str):
        response = dynamodb.scan(
            TableName=self._parameters.dag_state_table,
            FilterExpression="begins_with(#DAG, :dag) and execution_time = :execution_time",
            ProjectionExpression="#DAG",
            ExpressionAttributeNames={"#DAG": "name"},
            ExpressionAttributeValues={":dag": {"S": dag}, ":execution_time": {"S": execution_time}},
        )
        items = response["Items"]

        item_names = [item["name"]["S"] for item in items]

        return item_names

    def _get_item_statuses(self, dynamodb, execution_time: str, items):
        for items_subset in self._item_chunks(items, 25):
            get_requests = self._generate_get_requests(execution_time, items_subset)

            LOGGER.debug('Get Requests: %s', get_requests)

            response = dynamodb.batch_get_item(RequestItems={self._parameters.dag_state_table: get_requests})

            statuses = response["Responses"][collections.deque(response["Responses"].keys())[0]]

            return {status["name"]["S"]:status["status"]["S"] for status in statuses}

    def _clear_items(self, dynamodb, execution_time: str, items):
        for items_subset in self._item_chunks(items, 25):
            delete_requests = self._generate_delete_requests(execution_time, items_subset)
            LOGGER.debug('Delete Statements: %s', delete_requests)

            dynamodb.batch_write_item(RequestItems={self._parameters.dag_state_table: delete_requests})

    @classmethod
    def _item_chunks(cls, items, chunk_size):
        for index in range(0, len(items), chunk_size):
            yield items[index:index + chunk_size]

    @classmethod
    def _generate_get_requests(cls, execution_time: str, items: list):
        return dict(
            Keys=[
                dict(
                    name=dict(S=item),
                    execution_time=dict(S=execution_time)
                )
                for item in items
            ]
        )

    @classmethod
    def _generate_delete_requests(cls, execution_time: str, items: list):
        return [
            dict(
                DeleteRequest=dict(
                    Key=dict(
                        name=dict(S=item),
                        execution_time=dict(S=execution_time)
                    )
                )
            )
            for item in items
        ]

    @classmethod
    def _get_primary_key(cls, dag: str, task: str):
        primary_key = dag

        if task:
            primary_key += "__" + task

        return primary_key

    @classmethod
    def _get_lock_id(cls, primary_key: str, execution_time: str):
        return primary_key + "__" + execution_time

    def _get_status_from_state(self, dynamodb, primary_key: str, execution_time: str):
        status = Status.UNKNOWN

        state  = self._get_state(dynamodb, primary_key, execution_time)

        if "Item" in state:
            status = Status(state["Item"]["status"]["S"])

        return status

    def _set_status_if_later(self, dynamodb, primary_key: str, execution_time: str, status: Status):
        succeeded = False
        current_status = self._get_status_from_state(dynamodb, primary_key, execution_time)
        LOGGER.debug('Setting status of %s from %s to %s', primary_key, current_status, status)

        if status > current_status:
            self._set_state(dynamodb, primary_key, execution_time, status)

            succeeded = True

        return succeeded

    def _get_state(self, dynamodb, primary_key: str, execution_time: str):
        items = dynamodb.get_item(
            TableName=self._parameters.dag_state_table,
            Key=dict(
                name=dict(S=primary_key),
                execution_time=dict(S=execution_time)
            ),
            ConsistentRead=True
        )

        return items

    def _set_state(self, dynamodb, primary_key: str, execution_time: str, status: Status):
        dynamodb.put_item(
            TableName=self._parameters.dag_state_table,
            Item=dict(
                name=dict(S=primary_key),
                execution_time=dict(S=execution_time),
                status=dict(S=status.value)
            )
        )
