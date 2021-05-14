""" Convert a DAG schedule into a list of DAGs to run. """
from   abc import ABC, abstractmethod
from   dataclasses import dataclass
from   io import BytesIO

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
    state_plugin: str
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

    @classmethod
    def _determine_dags_to_run(cls, schedule):
        with AWSClient(
            'dynamodb',
            endpoint_url=self._parameters.endpoint_url,
            aws_access_key_id=self._parameters.access_key,
            aws_secret_access_key=self._parameters.secret_key,
            region_name=self._parameters.region_name
        ) as dynamodb:
            schedule["scheduled"] = [cls._is_scheduled(name, dynamodb) for name in schedule.name]

        return schedule.name[schedule.schedule == True]

    @classmethod
    def _is_scheduled(cls, name, dynamodb):
        pass
# import boto3
# import botocore.exceptions
#
# def lock(my_resource_id):
#     try:
#         # Put item with conditional expression to acquire the lock
#         dyn_table = boto3.resource('dynamodb').Table('my-lock-table')
#         dyn_table.put_item(
#             Item={'ResourceId': my_resource_id},
#             ConditionExpression="attribute_not_exists(#r)",
#             ExpressionAttributeNames={"#r": "ResourceId"})
#         # Lock acquired
#         return True
#     except botocore.exceptions.ClientError as e:
#         # Another exception than ConditionalCheckFailedException was caught, raise as-is
#         if e.response['Error']['Code'] != 'ConditionalCheckFailedException':
#             raise
#         else:
#             # Else, lock cannot be acquired because already locked
#             return False
