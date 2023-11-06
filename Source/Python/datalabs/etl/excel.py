""" Mixins for dealing with excel data """
from io import BytesIO

import pandas


class ExcelReaderMixin:
    @classmethod
    def _excel_to_dataframe(cls, data: bytes, **kwargs) -> pandas.DataFrame:
        return pandas.read_excel(BytesIO(data), engine="openpyxl", dtype="object", **kwargs)


class ExcelWriterMixin:
    @classmethod
    def _dataframe_to_excel(cls, data: pandas.DataFrame, **kwargs) -> bytes:
        return data.to_excel(index=False, engine="openpyxl", **kwargs)
