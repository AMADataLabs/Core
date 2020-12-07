""" Oneview Major Professional Activity Transformer"""
import logging

from   datalabs.etl.oneview.ppd.column import mpa_columns
from   datalabs.etl.oneview.transform import TransformerTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class MajorProfessionalActivityTransformerTask(TransformerTask):
    def _get_columns(self):
        return [mpa_columns]