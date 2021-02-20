""" AWS Secrets Manager access """
import json
import logging
import os

from   arnparse import arnparse
from   arnparse.arnparse import MalformedArnError
import boto3

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class SecretsManagerEnvironmentLoader:
    def __init__(self, secrets: dict, verify_ssl_certs=True):
        self._secrets = secrets
        self._secrets_manager = boto3.client('secretsmanager', verify=verify_ssl_certs)

    def load(self, environment: dict = None):
        if self._secrets:
            environment = environment or os.environ

            secret_values = self._get_secrets_from_secrets_manager()

            environment_variables = {key: json.dumps(value) for key, value in secret_values.items()}

            environment.update(environment_variables)

    @classmethod
    def from_environ(cls):
        verify_ssl_certs = str(os.environ.get('VERIFY_SSL_CERTS')).upper() != 'FALSE'
        arn_variables = {key:value for key, value in os.environ.items() if value.startswith('arn:')}

        secret_variables = cls._get_secrets_manager_arn_variables(arn_variables)
        LOGGER.info('Loaded values for the following Secrets Manager secrets: %s', secret_variables)

        return SecretsManagerEnvironmentLoader(secret_variables, verify_ssl_certs=verify_ssl_certs)

    def _get_secrets_from_secrets_manager(self):
        return {name:self._get_secret_from_secrets_manager(id) for name, id in self._secrets.items()}

    @classmethod
    def _get_secrets_manager_arn_variables(cls, arn_variables):
        secret_variables = dict()

        for key, value in arn_variables.items():
            try:
                arn = arnparse(value)

                if arn.service == 'secretsmanager' and arn.resource_type == 'secret':
                    secret_variables[key] = arn.resource.rsplit('-', 1)[0]
            except MalformedArnError:
                LOGGER.warning('Got Malformed ARN when processing Parameter Store environment variables: %s', value)

        return secret_variables

    # pylint: disable=redefined-builtin, invalid-name
    def _get_secret_from_secrets_manager(self, id):
        response = self._secrets_manager.get_secret_value(SecretId=id)

        return json.loads(response['SecretString'])
