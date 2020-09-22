import os

from   arnparse import arnparse
from   arnparse.arnparse import MalformedArnError
import boto3


class ParameterStoreEnvironmentLoader:
    def __init__(self, parameters: dict, verify_ssl_certs=True):
        self._parameters = parameters
        self._ssm = boto3.client('ssm', verify=verify_ssl_certs)

    def load(self, environment: dict=None):
        if self._parameters:
            environment = environment or os.environ

            parameter_store_keys = list(self._parameters.keys())

            parameter_values = self._get_parameters_from_parameter_store(parameter_store_keys)

            environment_variables = self._map_parameters_to_environment_variables(parameter_values)

            environment.update(environment_variables)

    @classmethod
    def from_environ(cls):
        verify_ssl_certs = str(os.environ.get('VERIFY_SSL_CERTS')).upper() != 'FALSE'
        arn_variables =  {key:value for key, value in os.environ.items() if value.startswith('arn:')}

        parameter_variables = cls._get_parameter_store_arn_variables(arn_variables)

        return ParameterStoreEnvironmentLoader(parameter_variables, verify_ssl_certs=verify_ssl_certs)

    def _get_parameters_from_parameter_store(self, parameter_store_keys):
        response = self._ssm.get_parameters(Names=parameter_store_keys, WithDecryption=True)

        return {parameter['Name']:parameter['Value'] for parameter in response['Parameters']}

    def _map_parameters_to_environment_variables(self, parameter_values):
        return {self._parameters[key]:value for key, value in parameter_values.items()}

    @classmethod
    def _get_parameter_store_arn_variables(cls, arn_variables):
        parameter_variables = dict()

        for key, value in arn_variables.items():
            try:
                arn = arnparse(value)

                if arn.service == 'ssm' and arn.resource_type == 'parameter':
                    parameter_variables[f'/{arn.resource}'] = key
            except MalformedArnError:
                pass

        return parameter_variables
