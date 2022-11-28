""" Mixins for dealing with CSV data """
from   io import BytesIO

import csv
import pandas


class CSVReaderMixin():
    @classmethod
    def _csv_to_dataframe(cls, data, **kwargs):
        return pandas.read_csv(BytesIO(data), dtype=object, **kwargs)


class CSVWriterMixin():
    @classmethod
    def _dataframe_to_csv(cls, data, **kwargs):
        print("_dataframe_to_csv **kwargssssssssssss", **kwargs)
        return data.to_csv(index=False, **kwargs).encode()

    @classmethod
    def _dataframe_to_txt(cls, data, **kwargs):
        return data.to_csv(header=None, index=None,doublequote=False,sep='\t',escapechar="",\
                quoting=csv.QUOTE_NONE,quotechar="",na_rep=" ",mode='a', **kwargs).encode()
