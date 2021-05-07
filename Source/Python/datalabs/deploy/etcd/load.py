""" Tool for loading Kubernetes ConfigMap data into etcd. """
import base64
import logging

import yaml

from   datalabs.access.etcd import Etcd

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class ConfigMapLoader():
    def __init__(self, etcd_config):
        self._etcd_config = etcd_config

    def load(self, filename):
        variables = self._extract_variables_from_configmap(filename)

        self._load_variables_into_etcd(variables)

    @classmethod
    def _extract_variables_from_configmap(cls, filename):
        with open(filename) as file:
            configmap = yaml.safe_load(file.read())

        return configmap['data']

    def _load_variables_into_etcd(self, variables):
        response = None
        transaction = self._generate_transaction_body(variables)

        with Etcd(self._etcd_config) as etcd:
            response = etcd.execute_transaction(transaction)

        return response

    @classmethod
    def _generate_transaction_body(cls, variables):
        return {
            "success": [
                {
                    "requestPut": {
                        "key": f"{base64.b64encode(key.encode('utf8')).decode('utf8')}",
                        "value": f"{base64.b64encode(value.encode('utf8')).decode('utf8')}"
                    }
                } for key, value in variables.items()
            ]
        }
