import os

import boto3


class ParameterStoreEnvironmentLoader:
    def __init__(self, parameters: dict, verify_ssl_certs=True):
        self._parameters = parameters
        self._ssm = boto3.client('ssm', verify=verify_ssl_certs)

    def load(self, environment: dict=None):
        environment = environment or os.environ
        parameter_store_keys = list(self._parameters.keys())

        parameter_values = self._get_parameters_from_parameter_store(parameter_store_keys)

        environment_variables = self._map_parameters_to_environment_variables(parameter_values)

        environment.update(environment_variables)

    def _get_parameters_from_parameter_store(self, parameter_store_keys):
        response = self._ssm.get_parameters(Names=parameter_store_keys, WithDecryption=True)

        return {parameter['Name']:parameter['Value'] for parameter in response['Parameters']}

    def _map_parameters_to_environment_variables(self, parameter_values):
        return {self._parameters[key]:value for key, value in parameter_values.items()}
