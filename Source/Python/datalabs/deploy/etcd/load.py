""" Tool for loading Kubernetes ConfigMap data into etcd. """
from   dataclasses import dataclass
import logging

import yaml

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


class ConfigMapLoader(ParameterValidatorMixin):
    PARAMETER_CLASS = EtcdParameters

    def __init__(self, etcd_config):
        self._etcd_config = self._get_validated_parameters(etcd_config)

    def load(self, filename):
        variables = self._extract_variables_from_configmap(filename)

        self._load_variables_in_etcd(variables)

    @classmethod
    def _extract_variables_from_configmap(cls, filename):
        with open(filename) as file:
            configmap = yaml.safe_load(file.read())

        return configmap['data']


    def _load_variables_in_etcd(self, variables):
        pass
