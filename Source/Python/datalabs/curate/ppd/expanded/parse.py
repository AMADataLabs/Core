"""File Parser for Expanded PPD"""
import io

import pandas

from   datalabs.curate.parse import Parser
from   datalabs.curate.ppd.expanded import column


class ExpandedPPDParser(Parser):
    # pylint: disable=arguments-differ
    def parse(self, text: bytes) -> pandas.DataFrame:
        return pandas.read_csv(
            io.BytesIO(text),
            sep='|',
            dtype=str,
            names=column.NAMES,
            index_col=False
        )
