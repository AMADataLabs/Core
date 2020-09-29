import logging
import os

from   arnparse import arnparse
from   arnparse.arnparse import MalformedArnError
import boto3

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class ParameterStoreEnvironmentLoader:
    def __init__(self, parameters: dict, verify_ssl_certs=True):
        self._parameters = parameters
        self._ssm = boto3.client('ssm', verify=verify_ssl_certs)

    def load(self, environment: dict=None):
        if self._parameters:
            environment = environment or os.environ

            parameter_values = self._get_parameters_from_parameter_store()

            environment_variables = self._map_parameters_to_environment_variables(parameter_values)

            environment.update(environment_variables)

    @classmethod
    def from_environ(cls):
        verify_ssl_certs = str(os.environ.get('VERIFY_SSL_CERTS')).upper() != 'FALSE'
        arn_variables =  {key:value for key, value in os.environ.items() if value.startswith('arn:')}

        parameter_variables = cls._get_parameter_store_arn_variables(arn_variables)
        LOGGER.info('Loaded values for the following Parameter Store parameters: %s', parameter_variables)

        return ParameterStoreEnvironmentLoader(parameter_variables, verify_ssl_certs=verify_ssl_certs)

    def _get_parameters_from_parameter_store(self):
        parameters = list(self._parameters.values())
        response = self._ssm.get_parameters(Names=parameters, WithDecryption=True)

        return {parameter['Name']:parameter['Value'] for parameter in response['Parameters']}

    def _map_parameters_to_environment_variables(self, parameter_values):
        return {key:parameter_values[value] for key, value in self._parameters.items()}

    @classmethod
    def _get_parameter_store_arn_variables(cls, arn_variables):
        parameter_variables = dict()

        for key, value in arn_variables.items():
            try:
                arn = arnparse(value)

                if arn.service == 'ssm' and arn.resource_type == 'parameter':
                    parameter_variables[key] = f'/{arn.resource}'
            except MalformedArnError:
                LOGGER.warn('Got Malformed ARN when processing Parameter Store environment variables: %s', value)

        return parameter_variables
