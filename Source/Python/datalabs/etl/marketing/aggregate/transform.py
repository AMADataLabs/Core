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

        if len(packed_data) == 0:
            return None

        input_files = self._extract_files(packed_data[0])

        input_data = self._read_input_data(input_files)

        input_data = self._clean_input_data(input_data)

        input_data_list = [input_data.adhoc,
                input_data.aims,
                input_data.list_of_lists,
                input_data.flatfile
        ]

        return [self._dataframe_to_csv(data) for data in input_data_list]

    def _parse(self, text, seperator = ','):
        decoded_text = self._decode(text)

        data = pandas.read_csv(io.StringIO(decoded_text),
                sep=seperator,
                on_bad_lines='skip',
                dtype=object,
                index_col=None
        )

        return data

    def _merge_adhoc_data(self, input_files: MarketingData):
        adhoc_files = []
        adhoc_data = input_files[0:-3]

        for data in adhoc_data:
            adhoc_file = self._parse(data, seperator = ',')
            adhoc_files.append(adhoc_file)

        return pandas.concat(adhoc_files, axis=0, ignore_index=True)

    def _read_input_data(self, input_files: []) -> MarketingData:

        adhoc = self._merge_adhoc_data(input_files)

        aims = self._parse(input_files[-3], seperator = '|')

        list_of_lists = self._parse(input_files[-2], seperator = ',')

        flatfile = self._parse(input_files[-1], seperator = '\t')

        return  MarketingData(adhoc, aims, list_of_lists, flatfile)

    @classmethod
    def _extract_files(cls, files):
        return [data for name, data in files]

    def _clean_input_data(self, input_data: MarketingData) -> MarketingData:
        input_data.adhoc = self._clean_adhoc(input_data.adhoc)

        input_data.aims = self._clean_aims(input_data.aims)

        input_data.list_of_lists = self._clean_list_of_lists(input_data.list_of_lists)

        input_data.flatfile = self._clean_flatfile(input_data.flatfile)

        return input_data


    @classmethod
    def _clean_adhoc(cls, adhoc):
        adhoc = adhoc.rename(columns={'EMAIL' : "BEST_EMAIL"})[
            [
                'CUSTOMER_ID',
                'NAME',
                'BUSTITLE',
                'BUSNAME',
                'ADDR1',
                'ADDR2',
                'ADDR3',
                'CITY',
                'STATE',
                'ZIP',
                'COUNTRY',
                'BEST_EMAIL',
                'DAY_PHONE',
                'EVENING_PHONE',
                'INDUSTRY_DESC'
                #'File_Name'
            ]
        ]

        return adhoc.dropna(subset=["BEST_EMAIL"])

    @classmethod
    def _clean_aims(cls, aims):
        columns = {
            '#AMA_Membership_Flag': 'MEMBERFLAG',
            'ME_Nbr': 'ME_Nbr',
            'Gender' : "GENDER",
            'Prim_Spec_Cd' : "AIMS_PRIMSPC",
            'Sec_Spec_Cd' : "AIMS_SECSPC",
            'Do_no_rent_flag' : "SUP_DNRFLAG",
            'Do_not_mail/email_flag' : "SUP_DNMFLAG",
            'Preferred_Email': 'BEST_EMAIL',
        }

        aims = aims.rename(columns=columns)[columns.values()]

        aims["PHYSICIANFLAG"] = "Y"

        return aims.dropna(subset=["BEST_EMAIL"])

    @classmethod
    def _clean_list_of_lists(cls, list_of_lists):
        list_of_lists = list_of_lists.rename(columns= {"LIST SOURCE KEY": "LISTKEY"})[
            [
                'LIST NUMBER',
                'CHANGED STATUS',
                'STATUS',
                'LISTKEY',
                'LIST NAME',
                'SOURCE'
            ]
        ]

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
