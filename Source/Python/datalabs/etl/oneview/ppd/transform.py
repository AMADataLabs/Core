""" Oneview PPD Transformer"""
import logging

from datalabs.etl.oneview.ppd.column import columns
from datalabs.etl.oneview.transform import TransformerTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class PPDDataFramesToCSVText(TransformerTask):
    def _transform(self):
        csv = super()._transform()

        return csv

    def _get_columns(self):
        return [columns]
