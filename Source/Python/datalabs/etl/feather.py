""" Mixins for dealing with CSV data """
from   io import BytesIO

import pandas


class FeatherReaderMixin():
    @classmethod
    def _feather_to_dataframe(cls, data: bytes, **kwargs) -> pandas.DataFrame:
        return pandas.read_feather(BytesIO(data), **kwargs)


class FeatherWriterMixin():
    @classmethod
    def _dataframe_to_feather(cls, data:  pandas.DataFrame, **kwargs) -> bytes:
        feather_data = BytesIO()

        data.to_feather(feather_data, **kwargs)

        return feather_data.getvalue()
