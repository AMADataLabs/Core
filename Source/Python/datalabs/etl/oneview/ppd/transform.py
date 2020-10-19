""" Oneview PPD Transformer"""
import logging
import pandas

from datalabs.etl.transform import TransformerTask
from datalabs.curate.parse import ParseToCSVTransformerTask
from datalabs.etl.parse.transform.ParseToCSVTransformerTask import parse as parser

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class PPDDataFramesToCSVText(ParseToCSVTransformerTask):
    def _transform(self):
        dataframe = self.parse(self._parameters.data)
        csv_data = self.to_csv(dataframe)
        return csv_data

    def _to_csv(self, dataframe):
        data = parser(dataframe)
        return data
