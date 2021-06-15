""" DynamoDB DAG state classes. """
from   dataclasses import dataclass
from   datetime import datetime
import time

import boto3
import botocore

from   datalabs.etl.dag.state.base import State, Status
from   datalabs.parameter import add_schema


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class StateParameters:
    state_lock_table: str
    state_table: str
    execution_time: str
    endpoint_url: str = None
    access_key: str = None
    secret_key: str = None
    region_name: str = None


class LockingState(State):
    PARAMETER_CLASS = StateParameters

    def connect(self):
        self._connection = boto3.client(
            'dynamodb',
            endpoint_url=self._parameters.endpoint_url,
            aws_access_key_id=self._parameters.access_key,
            aws_secret_access_key=self._parameters.secret_key,
            region_name=self._parameters.region_name
        )

    def _lock_state(self, name):
        lock_id = f'{name}-{self._parameters.execution_time}'
        locked = False

        try:
            table = self._connection.Table(self._parameters.state_lock_table)

            table.put_item(
                Item={'LockID': {'S': lock_id}, 'ttl': {'N': int(time.time()+30)}},
                ConditionExpression="attribute_not_exists(#r)",
                ExpressionAttributeNames={"#r": "LockID"}
            )

            locked = True
        except botocore.exceptions.ClientError as exception:
            if exception.response['Error']['Code'] != 'ConditionalCheckFailedException':
                raise

        return locked

    def _unlock_state(self, name):
        lock_id = f'{name}-{self._parameters.execution_time}'
        unlocked = False

        try:
            table = self._connection.Table(self._parameters.state_lock_table)

            table.delete_item(
                Key={'LockID': {'Value': {'S': lock_id}}},
                ConditionExpression="attribute_exists(#r)",
                ExpressionAttributeNames={"#r": "LockID"}
            )

            unlocked = True
        except botocore.exceptions.ClientError as exception:
            if exception.response['Error']['Code'] != 'ConditionalCheckFailedException':
                raise

        return unlocked

class DAGState(LockingState):
    def get_status(self, name: str, execution_time: datetime):
        state = None

        self._lock_state(name)

        table = self._connection.Table(self._parameters.state_table)
        state = table.get_item(
            Key=dict(name=name, execution_time=execution_time.isoformat()),
            ConsistantRead=True
        )

        self._unlock_state(name)

        return Status(state["Item"]["status"])

    def set_status(self, name: str, execution_time: datetime, status: Status):
        self._lock_state(name)

        table = self._connection.Table(self._parameters.state_table)
        table.put_item(
            Item=dict(
                name=dict(S=name),
                execution_time=dict(S=execution_time.isoformat()),
                status=dict(S=status.value)
            )
        )

        self._unlock_state(name)
