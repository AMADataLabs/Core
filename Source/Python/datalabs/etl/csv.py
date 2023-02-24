""" Mixins for dealing with CSV data """
from   io import BytesIO

import pandas


class CSVReaderMixin():
    @classmethod
    def _csv_to_dataframe(cls, data: bytes, **kwargs) -> pandas.DataFrame:
        return pandas.read_csv(BytesIO(data), dtype=object, **kwargs)


class CSVWriterMixin():
    @classmethod
    def _dataframe_to_csv(cls, data:  pandas.DataFrame, **kwargs) -> bytes:
        return data.to_csv(index=False, **kwargs).encode()
