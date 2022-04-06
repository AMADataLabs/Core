""" source: datalabs.etl.dag.plugin """
from   dataclasses import dataclass
import logging

from   datalabs.parameter import ParameterValidatorMixin
from   datalabs.etl.dag.plugin import PluginExecutorMixin
from   datalabs.parameter import add_schema

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=redefined-outer-name, protected-access
def test_parameters_without_unknowns_are_passed_to_init():
    parameters = TestParametersWithoutUnknowns("tick", "tock")
    executor = PluginExecutorMixin()

    plugin = executor._get_plugin("test.datalabs.etl.dag.test_plugin.TestPlugin", parameters)

    assert plugin.parameters.ping == "tick"
    assert plugin.parameters.pong == "tock"


# pylint: disable=redefined-outer-name, protected-access
def test_unknowns_are_passed_to_init():
    parameters = TestParametersWithUnknowns("tick", "tock", {"PITTER": "ding", "PATTER": "dong"})
    executor = PluginExecutorMixin()

    plugin = executor._get_plugin("test.datalabs.etl.dag.test_plugin.TestPlugin", parameters)

    assert plugin.parameters.ping == "tick"
    assert plugin.parameters.pong == "tock"
    assert plugin.parameters.pitter == "ding"
    assert plugin.parameters.patter == "dong"


@add_schema(unknowns=True)
@dataclass
class TestParametersWithoutUnknowns:
    ping: str
    pong: str


@add_schema(unknowns=True)
@dataclass
class TestParametersWithUnknowns:
    ping: str
    pong: str
    unknowns: dict=None


@add_schema(unknowns=True)
@dataclass
class TestPluginParameters:
    ping: str
    pong: str
    pitter: str=None
    patter: str=None


class TestPlugin(ParameterValidatorMixin):
    PARAMETER_CLASS = TestPluginParameters

    def __init__(self, parameters: dict):
        self._parameters = self._get_validated_parameters(parameters)

    @property
    def parameters(self):
        return self._parameters
