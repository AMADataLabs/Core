""" Automating cerner report task """
import logging

from   datalabs.task import Task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)



# pylint: disable=no-self-use
class CernerReportTransformerTask(Task):
    def run(self):
        LOGGER.info("Moving data")
