''' Hello world printing task implementation. '''
import logging
from datalabs.etl.transform import TransformerTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class HelloWorldTask(TransformerTask):
    ''' Hello world printing task class. '''
    def _transform(self):
        LOGGER.info("Hello world!")
