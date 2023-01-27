"""Expanded PPD transformer"""
from   datalabs.etl.parse.transform import ParseToCSVTransformerTask


class ParseToPPDTransformerTask(ParseToCSVTransformerTask):
    def run(self):
        data = super().run()

        data.append(data[0])

        return data
