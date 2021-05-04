"""Access environmental parameters"""
import base64
from   dataclasses import dataclass
import logging
import os

import requests

from   datalabs.task import add_schema

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class EtcdParameters:
    host: str
    prefix: str
    username: str
    password: str


class EtcdEnvironmentLoader:
    ''' Replace environment variable values that are AWS Systems Manager
        Parameter Store resource ARNs with the resource values.'''
    def __init__(self, parameters):
        self._parameters = self._get_validated_parameters(parameters)

    def load(self):
        parameters = self._get_parameters_from_etcd()

        self._set_environment_variables_from_parameters(parameters)

    @classmethod
    def _get_validated_parameters(cls, parameters: dict):
        parameter_variables = {key.lower():value for key, value in parameters.items()}
        schema = EtcdParameters.SCHEMA  # pylint: disable=no-member

        return schema.load(parameter_variables)

    def _get_parameters_from_etcd(self):
        with requests.Session() as etcd:
            token = self._authenticate(etcd)

            raw_parameters = self._get_raw_parameters_from_etcd(etcd, token)

            return self._extract_parameters(raw_parameters)

    @classmethod
    def _set_environment_variables_from_parameters(cls, parameters: dict):
        for key, value in parameters.items():
            os.environ[key] = value

    def _authenticate(self, etcd: requests.Session):
        body = dict(
            name=self._parameters.username,
            password=self._parameters.password
        )

        response = etcd.post(f'https://{self._parameters.host}/v3/auth/authenticate', json=body).json()

        return response['token']

    def _get_raw_parameters_from_etcd(self, etcd: requests.Session, token: str):
        range = self._parameters.prefix[:-1] + chr(ord(self._parameters.prefix[-1]) + 1)  # pylint: disable=redefined-builtin
        body = dict(
            key=base64.b64encode(self._parameters.prefix.encode('utf8')).decode('utf8'),
            range_end=base64.b64encode(range.encode('utf8')).decode('utf8')
        )

        etcd.headers = {"Authorization": token, "Content-Type": 'application/json'}

        response = etcd.post(f'https://{self._parameters.host}/v3/kv/range', json=body).json()

        if 'error' in response:
            raise EtcdException(response['message'])

        return response

    @classmethod
    def _extract_parameters(cls, raw_parameters):
        def decode(value):
            return base64.b64decode(value).decode('utf8')

        return {decode(p['key']):decode(p['value']) for p in raw_parameters['kvs']}


class EtcdException(Exception):
    pass
