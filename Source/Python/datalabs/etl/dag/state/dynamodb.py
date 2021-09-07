""" DynamoDB DAG state classes. """
from   dataclasses import dataclass
import time

import boto3
import botocore

from   datalabs.etl.dag.state.base import State, Status
from   datalabs.parameter import add_schema


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
    def _lock_state(self, dynamodb, lock_id):
        locked = False

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
        self._set_status(dag, None, execution_time, status)

    def set_task_status(self, dag: str, task: str, execution_time: str, status: Status):
        self._set_status(dag, task, execution_time, status)

    def _get_status(self, dag: str, task: str, execution_time: str):
        status = Status.UNKNOWN
        primary_key = self._get_primary_key(dag, task)
        lock_id = self._get_lock_id(primary_key, execution_time)
        state = None
        dynamodb = self._connect()

        self._lock_state(dynamodb, lock_id)

        state  = self._get_state(dynamodb, primary_key, execution_time)

        self._unlock_state(dynamodb, lock_id)

        if "Item" in state:
            status = Status(state["Item"]["status"]["S"])

        return status

    def _set_status(self, dag: str, task: str, execution_time: str, status: Status):
        primary_key = self._get_primary_key(dag, task)
        lock_id = self._get_lock_id(primary_key, execution_time)
        dynamodb = self._connect()

        self._lock_state(dynamodb, lock_id)

        self._set_state(dynamodb, primary_key, execution_time, status)

        self._unlock_state(dynamodb, lock_id)

    @classmethod
    def _get_primary_key(cls, dag: str, task: str):
        primary_key = dag

        if task:
            primary_key += "__" + task

        return primary_key

    @classmethod
    def _get_lock_id(cls, primary_key: str, execution_time: str):
        return primary_key + "__" + execution_time

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
