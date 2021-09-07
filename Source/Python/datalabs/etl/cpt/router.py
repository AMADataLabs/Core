""" CPT API ETL router for actions due to S3 data updates. """

from   dataclasses import dataclass
import json
import logging
import re

import boto3

from   datalabs.access.environment import VariableTree
import datalabs.awslambda as awslambda
from   datalabs.parameter import add_schema
import datalabs.task as task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@add_schema
@dataclass
class RouterParameters:
    event: dict
    base_path: str
    region: str
    account: str
    functions: str


class RouterTaskWrapper(awslambda.TaskWrapper):
    def _get_task_parameters(self):
        LOGGER.debug('Parameters: %s', self._parameters)
        parameters = dict(EVENT=self._parameters)  # foward the Lambda event to the task
        var_tree = VariableTree.from_environment()
        router_parameters = var_tree.get_branch_values(['ROUTER']) or {}

        parameters.update(router_parameters)

        return parameters

    def _handle_exception(self, exception: Exception):
        LOGGER.exception('Handling CPT ETL Router task exception: %s', exception)

    def _handle_success(self):
        LOGGER.info('CPT ETL Router task has finished')


class RouterTask(task.Task):
    PARAMETER_CLASS = RouterParameters

    def run(self):
        LOGGER.debug('Parameters: %s', self._parameters)
        for sns_record in self._parameters.event['Records']:
            sns_envelope = sns_record['Sns']
            message = json.loads(sns_envelope['Message'])
            s3_records = message['Records']

            for s3_record in s3_records:
                key = s3_record['s3']['object']['key']

                LOGGER.info('Object updated: %s', key)
                LOGGER.info('Matching against base path %s', self._parameters.base_path)

                match = re.match(self._parameters.base_path+'/([0-9]{8})/.*ETL_TRIGGER', key)
                if match:
                    LOGGER.info('Triggering with execution date: %s', match.group(1))
                    self._trigger_etls(match.group(1))
                else:
                    LOGGER.info('Ignoring non-trigger file update: %s', key)

        return 200, None

    def _trigger_etls(self, execution_date):
        client = boto3.client('lambda')
        region = self._parameters.region
        account = self._parameters.account
        functions = [f.strip() for f in self._parameters.functions.split(',')]

        for function in functions:
            LOGGER.info('Invoking function: %s', function)

            response = client.invoke(
                FunctionName=f'arn:aws:lambda:{region}:{account}:function:{function}',
                InvocationType='RequestResponse',
                Payload=json.dumps(dict(execution_time=f'{execution_date}T00:00:00+00:00'))
            )

        return response
