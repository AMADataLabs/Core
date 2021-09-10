"""File Parser for Expanded PPD"""
import io

import pandas

from   datalabs.curate.parse import Parser
import datalabs.curate.ppd.expanded.column as column


class ExpandedPPDParser(Parser):
    # pylint: disable=arguments-differ
    def parse(self, data: bytes) -> pandas.DataFrame:
        return pandas.read_csv(
            io.BytesIO(data),
            sep='|',
            dtype=str,
            names=column.NAMES,
            index_col=False
        )
