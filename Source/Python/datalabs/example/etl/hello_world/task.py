''' Hello world printing task implementation. '''
import logging
from   datalabs.task import Task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class HelloWorldTask(Task):
    ''' Hello world printing task class. '''
    def run(self):
        LOGGER.info("Hello world!")
