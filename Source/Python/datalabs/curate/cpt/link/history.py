"""CPT Link History Data Parser"""
import io
import logging
import pandas

from datalabs.curate.parse import Parser

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class CPTLinkParser(Parser):
    def __init__(self, column_names, header, separator=None):
        self._column_names = column_names
        self._separator = separator
        self._header = header

        if self._separator is None:
            self._separator = '\t'

    def parse(self, text: str) -> pandas.DataFrame:
        return pandas.read_csv(
            io.StringIO(text),
            names=self._column_names,
            sep=self._separator,
            header=self._header,
            dtype=str,
            skiprows=1
        )


class DeletionHistoryParser(CPTLinkParser):
    def __init__(self):
        super().__init__(
            ['concept_id', 'cpt_code', 'date_deleted', 'level', 'description', 'instruction'], header=0
        )


class CodeHistoryParser(CPTLinkParser):
    def __init__(self):
        super().__init__(
            ['date', 'change_type', 'concept_id', 'cpt_code', 'level', 'prior_value', 'current_value', 'instruction'], header=None
        )


class ModifierHistoryParser(CPTLinkParser):
    def __init__(self):
        super().__init__(
            ['date', 'change_type', 'concept_id', 'modifier_code', 'prior_value', 'current_value'], header=None
        )
