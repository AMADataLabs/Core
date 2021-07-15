""" DynamoDB DAG state classes. """
from   dataclasses import dataclass
from   datetime import datetime
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
    def _lock_state(self, dynamodb, name):
        lock_id = f'{name}-{self._parameters.execution_time}'
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

    def _unlock_state(self, dynamodb, name):
        lock_id = f'{name}-{self._parameters.execution_time}'
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
    dag: str
    state_lock_table: str
    dag_state_table: str
    execution_time: str
    task: str=None
    endpoint_url: str=None
    access_key: str=None
    secret_key: str=None
    region_name: str=None
    unknowns: dict=None


class DAGState(DynamoDBClientMixin, LockingStateMixin, State):
    PARAMETER_CLASS = DAGStateParameters

    def get_status(self):
        status = Status.UNKNOWN
        lock_id = self._get_primary_key()
        state = None
        dynamodb = self._connect()

        self._lock_state(dynamodb, lock_id)

        state  = self._get_state(dynamodb)

        self._unlock_state(dynamodb, lock_id)

        if "Item" in state:
            status = Status(state["Item"]["status"]["S"])

        return status

    def set_status(self, status: Status):
        lock_id = self._get_primary_key()
        dynamodb = self._connect()

        self._lock_state(dynamodb, lock_id)

        self._set_state(dynamodb, status)

        self._unlock_state(dynamodb, lock_id)

    def _get_state(self, dynamodb):
        items = dynamodb.get_item(
            TableName=self._parameters.dag_state_table,
            Key=dict(
                name=dict(S=self._get_primary_key()),
                execution_time=dict(S=self._parameters.execution_time)
            ),
            ConsistentRead=True
        )

        #                 DAG=dict(S=self._parameters.dag)

        return items


    def _set_state(self, dynamodb, status: Status):
        dynamodb.put_item(
            TableName=self._parameters.dag_state_table,
            Item=dict(
                name=dict(S=self._get_primary_key()),
                execution_time=dict(S=self._parameters.execution_time),
                DAG=dict(S=self._parameters.dag),
                status=dict(S=status.value)
            )
        )

    def _get_primary_key(self):
        lock_id = self._parameters.dag

        if self._parameters.task:
            lock_id += "__" + self._parameters.task

        return lock_id
