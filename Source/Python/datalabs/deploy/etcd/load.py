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

        return [(key, value) for key, value in configmap['data'].items()]

    def _load_variables_into_etcd(self, variables):
        chunk_size = 100
        responses = []
        transactions = [
            self._generate_transaction_body(variables[i:i + chunk_size])
            for i in range(0, len(variables), chunk_size)
        ]
        # transaction = self._generate_transaction_body(variables)

        with Etcd(self._etcd_config) as etcd:
            for transaction in transactions:
                responses.append(etcd.execute_transaction(transaction))

        return responses

    @classmethod
    def _generate_transaction_body(cls, variables):
        return {
            "success": [
                {
                    "requestPut": {
                        "key": f"{base64.b64encode(key.encode('utf8')).decode('utf8')}",
                        "value": f"{base64.b64encode(value.encode('utf8')).decode('utf8')}"
                    }
                } for key, value in variables
            ]
        }
