from   dataclasses import dataclass
import json
import logging
import re

import boto3

from   datalabs.access.environment import VariableTree
import datalabs.task as task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


@task.add_schema
@dataclass
class RouterParameters:
    event: dict
    base_path: str
    region: str
    account: str
    functions: str


class RouterTaskWrapper(task.TaskWrapper):
    def _get_task_parameters(self):
        parameters = dict(EVENT=self._parameters)  # foward the Lambda event to the task
        var_tree = VariableTree.generate()
        router_parameters = var_tree.get_branch_values(['ROUTER']) or {}

        parameters.update(router_parameters)

        return parameters

    def _handle_exception(self, exception: ETLException):
        LOGGER.exception('Handling CPT ETL Router task exception: %s', exception)

    def _handle_success(self):
        LOGGER.info('CPT ETL Router task has finished')


class RouterTask(task.Task):
    PARAMETER_CLASS = RouterParameters

    def run(self):
        for sns_record in self._parameters.event['Records']:
            sns_envelope = sns_record['Sns']
            message = json.loads(sns_envelope['Message'])
            s3_records = message['Records']

            for s3_record in s3_records:
                key = s3_record['s3']['object']['key']
                base_path = self._parameters.base_path

                LOGGER.info(f'Object updated: %s', key)

                match = re.match(base_path+'/([0-9]{8})/.*ETL_TRIGGER', key)
                if match:
                    LOGGER.info(f'Triggering with execution date: {match.group(1)}')
                    self._trigger_etls(match.group(1))
                else:
                    LOGGER.info(f'Ignoring non-trigger file update: {key}')

        return 200, None

    def _trigger_etls(execution_date):
        client = boto3.client('lambda')

        for function in self._parameters.functions:
            LOGGER.info(f'Invoking function: {function}')

            response = client.invoke(
                FunctionName = f'arn:aws:lambda:{self._parameters.region}:{self._parameters.account}:function:{function}',
                InvocationType = 'RequestResponse',
                Payload = json.dumps(dict(execution_time=f'{execution_date}T00:00:00+00:00'))
            )
