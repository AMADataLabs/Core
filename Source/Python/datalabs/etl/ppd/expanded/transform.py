"""Expanded PPD transformer"""
from   datalabs.etl.parse.transform import ParseToCSVTransformerTask


class ParseToPPDTransformerTask(ParseToCSVTransformerTask):
    def _transform(self):
        data = super()._transform()

        data.append(data[0])

        return data
