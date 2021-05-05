""" Client classes for etcd """
from   dataclasses import dataclass
import logging

import requests

from   datalabs.access.datastore import Datastore
from   datalabs.access.credentials import Credentials
from   datalabs.task import add_schema, ParameterValidatorMixin

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


class Etcd(Datastore):
    PARAMETER_CLASS = EtcdParameters

    def __init__(self, etcd_config):
        self._etcd_config = self._get_validated_parameters(etcd_config)
        self._token = None

    def connect(self):
        self._connection = requests.Session()

        self._authenticate

    def _authenticate(self, etcd: requests.Session):
        body = dict(
            name=self._parameters.username,
            password=self._parameters.password
        )

        response = etcd.post(f'https://{self._parameters.host}/v3/auth/authenticate', json=body).json()

        etcd.headers = {
            "Authorization": response['token'],
            "Content-Type": "application/json"
        }

    def _execute_transaction(self, transaction: dict):
        response = self._connection.post(f'https://{self._parameters.host}/v3/kv/txn', json=transaction).json()

        if 'error' in response:
            raise EtcdException(response['message'])

        return response


class EtcdException(Exception):
    pass
