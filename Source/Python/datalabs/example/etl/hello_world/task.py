''' Hello world printing task implementation. '''
from   dataclasses import dataclass
import logging

from mpmath import mp
from   datalabs.task import Task
from   datalabs.parameter import add_schema


logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


@add_schema(unknowns=True)
@dataclass
class HelloWorldParameters:
    first_name: str
    last_name: str


class HelloWorldTask(Task):
    ''' Hello world printing task class. '''
    PARAMETER_CLASS = HelloWorldParameters

    def run(self):
        mp.dps = 50
        sqrt_2 = mp.sqrt(2)
        LOGGER.info('Hello, %s %s! The square root of 2 = %f', self._parameters.first_name, self._parameters.last_name, sqrt_2)

