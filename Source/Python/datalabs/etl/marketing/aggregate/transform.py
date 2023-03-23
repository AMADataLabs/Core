"""Transformer task for running marketing aggregator"""
from   dataclasses import dataclass
import io
import logging
import pickle

import pandas

from   datalabs.etl.task import ExecutionTimeMixin
from   datalabs.parameter import add_schema
from   datalabs.task import Task

from   datalabs.etl.manipulate.transform import DataFrameTransformerMixin
from   datalabs.etl.marketing.aggregate.column import ADHOC_COLUMNS,AIMS_COLUMNS,LIST_OF_LISTS_COLUMNS

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class EmailValidatorTask:
    pass


@dataclass
class MarketingData:
    adhoc: pandas.DataFrame
    aims: pandas.DataFrame
    list_of_lists: pandas.DataFrame
    flatfile: pandas.DataFrame


@add_schema
@dataclass
class InputDataCleanerTaskParameters:
    execution_time: str = None


class InputDataCleanerTask(ExecutionTimeMixin, DataFrameTransformerMixin, Task):
    PARAMETER_CLASS = InputDataCleanerTaskParameters

    def run(self):
        packed_data = [pickle.loads(pickled_dataset) for pickled_dataset in self._data]
        try:
            input_data = self._read_input_data(packed_data[0])
            input_data = self._clean_input_data(input_data)

            input_data_list = [
                input_data.adhoc,
                input_data.aims,
                input_data.list_of_lists,
                input_data.flatfile
            ]
            return [self._dataframe_to_csv(data) for data in input_data_list]

        except IndexError:
            input_data = []

        return []

    def _parse(self, text, seperator = ','):
        decoded_text = self._decode(text)

        data = pandas.read_csv(
            io.StringIO(decoded_text),
            sep=seperator,
            on_bad_lines='skip',
            dtype=object,
            index_col=None
        )

        return data

    def _merge_adhoc_data(self, input_files: MarketingData):
        adhoc_files = []
        adhoc_data = input_files[0:-3]

        for name, data in adhoc_data:
            adhoc_file = self._parse(data, seperator = ',')
            adhoc_file['File_Name'] = name
            adhoc_files.append(adhoc_file)

        return pandas.concat(adhoc_files, axis=0, ignore_index=True)

    def _read_input_data(self, input_files: []) -> MarketingData:

        adhoc = self._merge_adhoc_data(input_files)

        aims = self._parse(input_files[-3][1], seperator = '|')

        list_of_lists = self._parse(input_files[-2][1], seperator = ',')

        flatfile = self._parse(input_files[-1][1], seperator = '\t')

        return  MarketingData(adhoc, aims, list_of_lists, flatfile)

    def _clean_input_data(self, input_data: MarketingData) -> MarketingData:
        input_data.adhoc = self._clean_adhoc(input_data.adhoc)

        input_data.aims = self._clean_aims(input_data.aims)

        input_data.list_of_lists = self._clean_list_of_lists(input_data.list_of_lists)

        input_data.flatfile = self._clean_flatfile(input_data.flatfile)

        return input_data


    @classmethod
    def _clean_adhoc(cls, adhoc):
        adhoc = adhoc.rename(columns=ADHOC_COLUMNS)[ADHOC_COLUMNS.values()]

        return adhoc.dropna(subset=["BEST_EMAIL"])

    @classmethod
    def _clean_aims(cls, aims):
        aims = aims.rename(columns=AIMS_COLUMNS)[AIMS_COLUMNS.values()]

        aims["PHYSICIANFLAG"] = "Y"

        return aims.dropna(subset=["BEST_EMAIL"])

    @classmethod
    def _clean_list_of_lists(cls, list_of_lists):
        list_of_lists = list_of_lists.rename(columns=LIST_OF_LISTS_COLUMNS)[LIST_OF_LISTS_COLUMNS.values()]
        list_of_lists["LISTKEY"] = list_of_lists["LISTKEY"] + "#"

        return list_of_lists

    @classmethod
    def _clean_flatfile(cls, flatfile):
        flatfile["EMPPID"] = flatfile["EMPPID"].astype(int)

        return flatfile.fillna('')

    @classmethod
    def _decode(cls, text):
        decoded_text = None

        try:
            decoded_text = text.decode()
        except UnicodeDecodeError:
            decoded_text = text.decode('cp1252', errors='backslashreplace')

        return decoded_text


class UniqueEmailsIdentifierTask:
    pass


class NewEmailsIdentifierTask:
    pass


class FlatFileGeneratorTask:
    pass


class ListKeysCompilerTask:
    pass


class SFMCLoaderTask:
    pass


class SFTPLoaderTask:
    pass
