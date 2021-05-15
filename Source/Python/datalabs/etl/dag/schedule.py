""" Convert a DAG schedule into a list of DAGs to run. """
from   abc import ABC, abstractmethod
from   dataclasses import dataclass
from   io import BytesIO

import botocore.exceptions
import csv
import logging
import pandas

import datalabs.etl.transform as etl
from   datalabs.parameter import add_schema

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class DAGScheduleTransformerParameters:
    state_lock_table: str
    dag_state_table: str
    endpoint_url: str = None
    access_key: str = None
    secret_key: str = None
    region_name: str = None
    execution_time: str = None
    data: object = None


class DAGScheduleTransformerTask(etl.ExecutionTimeMixin, etl.TransformerTask):
    PARAMETER_CLASS = DAGScheduleTransformerParameters

    def _transform(self):
        LOGGER.info(self._parameters['data'])
        schedule = None

        try:
            schedule = pandas.read_csv(BytesIO(self._parameters['data'][0]))
        except Exception as exception:
            raise ValueError('Bad schedule data: %s', self._parameters['data']) from exception

        dag_names = self._determine_dags_to_run(schedule)

        return [data.encode('utf-8', errors='backslashreplace') for data in dag_names]

    def _determine_dags_to_run(self, schedule):
        with AWSClient(
            'dynamodb',
            endpoint_url=self._parameters.endpoint_url,
            aws_access_key_id=self._parameters.access_key,
            aws_secret_access_key=self._parameters.secret_key,
            region_name=self._parameters.region_name
        ) as dynamodb:
            schedule["started"] = [self._is_scheduled(name, dynamodb) for name in schedule.name]

        return schedule.name[schedule.started == False]

    def _is_started(self, dynamodb, name):
        self._lock_state(dynamodb, name)

        state = self._get_state(dynamodb, name)

        self._unlock_state(dynamodb, name)

        return state["status"] == 'Pending' or state["status"] == 'Started'

    def _lock_state(self, dynamodb, name):
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
