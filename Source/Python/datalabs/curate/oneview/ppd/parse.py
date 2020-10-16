"""Parser for Oneview PPD"""
import pandas

from datalabs.curate.parse import Parser
import datalabs.curate.oneview.ppd.columns as columns


class ExpandedPPDParser(Parser):
    def parse(self, data: pandas.DataFrame) -> pandas.DataFrame:
        data.columns = columns
        return data
