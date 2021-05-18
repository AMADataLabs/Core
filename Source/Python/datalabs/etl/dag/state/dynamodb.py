""" DynamoDB DAG state classes. """
from   dataclasses import dataclass

from   datalabs.etl.dag.state.base import State
from   datalabs.parameter import add_schema


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class DAGStateParameters:
    state_lock_table: str
    dag_state_table: str
    task_state_table: str
    execution_time: str
    endpoint_url: str = None
    access_key: str = None
    secret_key: str = None
    region_name: str = None


class DAGState(State):
    def __init__(self):
        self._dynamodb = None

    def connect(self):
        with AWSClient(
            'dynamodb',
            endpoint_url=self._parameters.endpoint_url,
            aws_access_key_id=self._parameters.access_key,
            aws_secret_access_key=self._parameters.secret_key,
            region_name=self._parameters.region_name
        ) as dynamodb:
        self._dynamodb =

    def lock_state(self, dynamodb, name):
        lock_id = f'{name}-{self._parameters.execution_time}'
        locked = False

        try:
            table = dynamodb.Table(self._parameters.state_lock_table)

            table.put_item(
                Item={'LockID': {'S': lock_id}, 'ttl': {'N': int(time.time()+30)}},
                ConditionExpression="attribute_not_exists(#r)",
                ExpressionAttributeNames={"#r": "LockID"})

            locked = True
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] != 'ConditionalCheckFailedException':
                raise
            else:
                pass

        return locked

    def _get_state(self, dynamodb, name):
        pass

    def _unlock_state(self, dynamodb, name):
        lock_id = f'{name}-{self._parameters.execution_time}'
        unlocked = False

        try:
            table = dynamodb.Table(self._parameters.state_lock_table)

            table.delete_item(
                Key={'LockID': {'Value': {'S': lock_id}}},
                ConditionExpression="attribute_exists(#r)",
                ExpressionAttributeNames={"#r": "LockID"})

            unlocked = True
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] != 'ConditionalCheckFailedException':
                raise
            else:
                pass

        return unlocked
