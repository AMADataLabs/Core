""" Raw data cleaning transformer tasks for AIMS, EDW, and ODS """
# pylint: disable=import-error
from   dataclasses import dataclass

import pandas as pd

from   datalabs.etl.csv import CSVReaderMixin, CSVWriterMixin
from   datalabs.parameter import add_schema
from   datalabs.task import Task


class DataCleanerMixin:
    @classmethod
    def _clean_data(cls, data: pd.DataFrame) -> pd.DataFrame:
        data.columns = [col.lower() for col in data.columns]

        for col in data.columns:
            data[col] = data[col].fillna('').astype(str).apply(str.strip).apply(
                lambda x: x[:-2] if x.endswith('.0') else x
            )

        return data


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class DatabaseTableCleanupTransformerParameters:
    keep_columns: str = None
    clean_whitespace: str = None
    date_columns: str = None
    repair_datetime: str = None
    convert_to_int_columns: str = None
    rename_columns: str = None
    execution_time: str = None


class DatabaseTableCleanupTransformerTask(CSVReaderMixin, CSVWriterMixin, DataCleanerMixin, Task):
    PARAMETER_CLASS = DatabaseTableCleanupTransformerParameters

    def run(self) -> 'list<bytes>':
        data = self._csv_to_dataframe(self._data[0], sep=',', dtype=str, encoding='latin')

        if len(data.columns.values) == 1 and '|' in data.columns.values[0]:  # pylint: disable=no-member
            self._csv_to_dataframe(self._data[0], sep='|', dtype=str, encoding='latin')

        transformed_data = self._transform(data)

        return [self._dataframe_to_csv(transformed_data, sep='|')]

    # pylint: disable=too-many-statements
    def _transform(self, data):
        col0 = data.columns[0]
        results = pd.DataFrame()

        try:
            if all(data[col0].astype(int) == data.index):
                print('data contained index column. removing.')
                del data[col0]
        except:  # pylint: disable=bare-except
            pass

        if str(self._parameters.keep_columns).upper() not in ['', 'NONE']:
            keep_columns = self._parameters.keep_columns.split(',')
            for col in keep_columns:
                results[col] = data[col].copy()
        else:
            results = data.copy()

        if str(self._parameters.clean_whitespace).upper() == 'TRUE':
            results = self.clean_whitespace(results)

        if str(self._parameters.date_columns).upper() not in ['', 'None']:
            cols = self._parameters.date_columns.split(',')

            for col in cols:
                if str(self._parameters.repair_datetime).upper() == 'TRUE':
                    results[col] = results[col].apply(self.repair_datetime)
                results[col] = pd.to_datetime(results[col])

        if str(self._parameters.convert_to_int).upper() not in ['', 'NONE']:
            cols = self._parameters.convert_to_int_columns.split(',')

            for col in cols:
                results[col] = results[col].apply(self.convert_to_int)

        if str(self._parameters.rename_columns).upper() not in ['', 'NONE']:
            cols = self._parameters.rename_columns.split(',')

            results.columns = cols

        return results

    @classmethod
    def clean_whitespace(cls, data: pd.DataFrame, reduce=True):
        for col in data.columns.values:
            if reduce:
                data[col] = data[col].apply(lambda x: ' '.join(x.strip().split()) if isinstance(x, str) else x)
            else:
                data[col] = data[col].apply(lambda x: x.strip() if isinstance(x, str) else x)

        return data

    @classmethod
    def repair_datetime(cls, text):
        if not isinstance(text, str):
            return text
        text = text.strip()
        if len(text) > 10 and text[4] == '/' and text[10] == ':':
            result = text[:10].strip() + ' ' + text[11:].strip()
            return result
        tokens = text.split()
        if len(tokens) > 1 and tokens[1].startswith(':'):
            tokens[1] = tokens[1][1:].strip()
            return ' '.join(tokens)

        return text

    @classmethod
    def convert_to_int(cls, text):
        if isinstance(text, str) and text.isdigit():
            result = str(text)
        elif isinstance(text, float) and str(text).endswith('.0'):
            result = str(text)[:-2]
        else:
            result = text

        return result
