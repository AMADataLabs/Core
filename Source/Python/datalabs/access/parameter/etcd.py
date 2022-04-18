"""Access environmental parameters"""
import base64
from   dataclasses import dataclass
import logging
import os

import requests

from   datalabs.access.etcd import EtcdException
from   datalabs.parameter import add_schema, ParameterValidatorMixin

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


class EtcdEnvironmentLoader(ParameterValidatorMixin):
    PARAMETER_CLASS = EtcdParameters

    def __init__(self, parameters):
        self._parameters = self._get_validated_parameters(parameters)

    def load(self):
        parameters = self._get_parameters_from_etcd()

        self._set_environment_variables_from_parameters(parameters)

    @classmethod
    def from_environ(cls):
        host = os.environ.get('ETCD_HOST')
        username = os.environ.get('ETCD_USERNAME')
        password = os.environ.get('ETCD_PASSWORD')
        prefix = os.environ.get('ETCD_PREFIX')
        loader = None

        if host and username and password and prefix:
            loader = EtcdEnvironmentLoader(dict(
                host=host,
                username=username,
                password=password,
                prefix=prefix
            ))

        return loader

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

        if 'error' in response:
            raise EtcdException(response['message'])

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
        parameters = {}

        def decode(value):
            return base64.b64decode(value).decode('utf8')

        if 'kvs' in raw_parameters:
            parameters = {decode(p['key']):decode(p['value']) for p in raw_parameters['kvs']}

        return parameters
