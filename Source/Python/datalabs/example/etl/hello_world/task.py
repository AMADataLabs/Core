''' Hello world printing task implementation. '''
from   dataclasses import dataclass

import logging
from datalabs.task import Task
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
        LOGGER.info(f'First name: {self._parameters.first_name}; Last name: {self._parameters.last_name}')
