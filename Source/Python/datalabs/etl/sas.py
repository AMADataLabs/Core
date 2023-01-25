""" Mixins for dealing with CSV data """
from   io import BytesIO

import pandas


class SASReaderMixin():
    @classmethod
    def _sas_to_dataframe(cls, data: bytes, **kwargs) -> pandas.DataFrame:
        return pandas.read_sas(BytesIO(data), **kwargs)
