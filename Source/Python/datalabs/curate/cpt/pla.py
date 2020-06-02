import logging

import pandas

from datalabs.curate.parse import Parser


class PLAParser(Parser):
    def parse(self, text: str) -> pandas.DataFrame:
        return pandas.DataFrame(dict(code=['00000'], descriptor=['N/A']))
