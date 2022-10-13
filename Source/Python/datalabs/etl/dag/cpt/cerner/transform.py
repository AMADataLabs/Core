""" Automating cerner report task """
import logging


# pylint: disable=import-error, invalid-name
from datalabs.etl.transform import TransformerTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)



# pylint: disable=no-self-use
class CernerReportTransformerTask(TransformerTask):
    def _transform(self):
        LOGGER.info("Moving data")
