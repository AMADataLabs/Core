""" Utility functions for curating data in Pandas DataFrames. """
import pandas as pd


@pd.api.extensions.register_dataframe_accessor("datalabs")
class DatalabsAccessor:
    def __init__(self, data):
        self._data = data

    def rename_in_upper_case(self):
        """ Like DataFrame.rename() but new names are the old names converted to upper case. """
        column_names = self._data.columns.values
        column_name_map = {name:name.upper() for name in column_names}

        return self._data.rename(columns=column_name_map)

    def upper(self):
        """ Convert all string values in the DataFrame to upper case. """
        column_names = self._data.columns[self._data.dtypes == 'object']

        self._data[column_names] = self._data[column_names].apply(lambda column: column.str.upper())

        return self._data

    def strip(self):
        """ Apply string.strip() to all string values in the DataFrame. """
        column_names = self._data.columns[self._data.dtypes == 'object']

        self._data[column_names] = self._data[column_names].apply(lambda column: column.str.strip())

        return self._data
