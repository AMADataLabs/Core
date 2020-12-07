""" Oneview PPD Transformer"""
import logging

from   datalabs.etl.oneview.ppd.column import PPD_COLUMNS
from   datalabs.etl.oneview.transform import TransformerTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class PPDTransformerTask(TransformerTask):
    def _get_columns(self):
        return [PPD_COLUMNS]
