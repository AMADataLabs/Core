""" Client classes for etcd """
from   dataclasses import dataclass
import logging

import requests

from   datalabs.access.datastore import Datastore
from   datalabs.parameter import add_schema, ParameterValidatorMixin

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class EtcdParameters:
    host: str
    username: str
    password: str


class Etcd(ParameterValidatorMixin, Datastore):
    PARAMETER_CLASS = EtcdParameters

    def __init__(self, parameters):
        super().__init__()

        self._parameters = self._get_validated_parameters(parameters)
        self._token = None

    def connect(self):
        self._connection = requests.Session()

        self._authenticate()

    def execute_transaction(self, transaction: dict):
        response = self._connection.post(f'https://{self._parameters.host}/v3/kv/txn', json=transaction).json()

        if 'error' in response:
            raise EtcdException(response['message'])

        return response

    def _authenticate(self):
        body = dict(
            name=self._parameters.username,
            password=self._parameters.password
        )

        response = self._connection.post(f'https://{self._parameters.host}/v3/auth/authenticate', json=body).json()

        self._connection.headers = {
            "Authorization": response['token'],
            "Content-Type": "application/json"
        }


class EtcdException(Exception):
    pass
