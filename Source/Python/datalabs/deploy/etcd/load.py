""" Tool for loading Kubernetes ConfigMap data into etcd. """
from   dataclasses import dataclass
import logging

import requests
import yaml

from   datalabs.access.etcd import Etcd, EtcdException

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class ConfigMapLoader():
    PARAMETER_CLASS = EtcdParameters

    def __init__(self, etcd_config):
        self._etcd_config = etcd_config

    def load(self, filename):
        variables = self._extract_variables_from_configmap(filename)

        self._load_variables_in_etcd(variables)

    @classmethod
    def _extract_variables_from_configmap(cls, filename):
        with open(filename) as file:
            configmap = yaml.safe_load(file.read())

        return configmap['data']

    def _load_variables_into_etcd(self, variables):
        response = None
        transaction = self._generate_transaction_body()

        with Etcd(self._etcd_config) as etcd:
            response = etcd.execute_transaction(transaction)

        return response

    def _generate_transaction_body(self):
        pass
