""" Oneview PPD Transformer"""
import logging

from datalabs.curate.parse import ParseToCSVTransformerTask


logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class PPDDataFramesToCSVText(ParseToCSVTransformerTask):
    def _transform(self):
        data = super()._transform()
        data.append(data[0])

        return data
