""" Mixins for dealing with CSV data """
from   io import BytesIO

import pandas


class ParquetReaderMixin():
    @classmethod
    def _parquet_to_dataframe(cls, data: bytes, **kwargs) -> pandas.DataFrame:
        return pandas.read_parquet(BytesIO(data), **kwargs)


class ParquetWriterMixin():
    @classmethod
    def _dataframe_to_parquet(cls, data:  pandas.DataFrame, **kwargs) -> bytes:
        return data.to_parquet(index=False, **kwargs)
