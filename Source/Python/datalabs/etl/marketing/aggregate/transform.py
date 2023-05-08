"""Transformer task for running marketing aggregator"""
from   dataclasses import dataclass
from   datetime import datetime
import io
import logging
import os
import pickle

import pandas

from   datalabs.access.atdata import AtData
from   datalabs.etl.manipulate.transform import DataFrameTransformerMixin
from   datalabs.etl.marketing.aggregate import column
from   datalabs.etl.task import ExecutionTimeMixin
from   datalabs.parameter import add_schema
from   datalabs.task import Task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class InputDataParser:
    @classmethod
    def parse(cls,text, seperator = ','):
        decoded_text = cls._decode(text)

        data = pandas.read_csv(
            io.StringIO(decoded_text),
            sep=seperator,
            on_bad_lines='skip',
            dtype=object,
            index_col=None
        )

        return data

    @classmethod
    def _decode(cls, text):
        decoded_text = None

        try:
            decoded_text = text.decode()
        except UnicodeDecodeError:
            decoded_text = text.decode('cp1252', errors='backslashreplace')

        return decoded_text


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

        input_data = self._read_input_data(packed_data[0])

        input_data = self._clean_input_data(input_data)

        input_data_list = [
            input_data.adhoc,
            input_data.aims,
            input_data.list_of_lists,
            input_data.flatfile
        ]

        return [self._dataframe_to_csv(data) for data in input_data_list]

    def _read_input_data(self, input_files: []) -> MarketingData:
        adhoc = self._merge_adhoc_data(input_files)

        aims = InputDataParser.parse(input_files[-3][1], seperator = '|')

        list_of_lists = InputDataParser.parse(input_files[-2][1], seperator = ',')

        flatfile = InputDataParser.parse(input_files[-1][1], seperator = '\t')

        return  MarketingData(adhoc, aims, list_of_lists, flatfile)

    def _clean_input_data(self, input_data: MarketingData) -> MarketingData:
        input_data.adhoc = self._clean_adhoc(input_data.adhoc)

        input_data.aims = self._clean_aims(input_data.aims)

        input_data.list_of_lists = self._clean_list_of_lists(input_data.list_of_lists)

        input_data.flatfile = self._clean_flatfile(input_data.flatfile)

        return input_data

    @classmethod
    def _merge_adhoc_data(cls, input_files: MarketingData):
        adhoc_files = []
        adhoc_data = input_files[0:-3]

        for name, data in adhoc_data:
            adhoc_file = InputDataParser.parse(data, seperator = ',')
            adhoc_file['File_Name'] = os.path.basename(os.path.normpath(name))
            adhoc_files.append(adhoc_file)

        return pandas.concat(adhoc_files, axis=0, ignore_index=True)

    @classmethod
    def _clean_adhoc(cls, adhoc):
        adhoc = adhoc.rename(columns=column.ADHOC_COLUMNS)[column.ADHOC_COLUMNS.values()]

        return adhoc.dropna(subset=["BEST_EMAIL"])

    @classmethod
    def _clean_aims(cls, aims):
        aims = aims.rename(columns=column.AIMS_COLUMNS)[column.AIMS_COLUMNS.values()]

        aims["PHYSICIANFLAG"] = "Y"

        return aims.dropna(subset=["BEST_EMAIL"])

    @classmethod
    def _clean_list_of_lists(cls, list_of_lists):
        list_of_lists = list_of_lists.rename(columns=\
                column.LIST_OF_LISTS_COLUMNS)[column.LIST_OF_LISTS_COLUMNS.values()]
        list_of_lists["LISTKEY"] = list_of_lists["LISTKEY"] + "#"

        return list_of_lists

    @classmethod
    def _clean_flatfile(cls, flatfile):
        flatfile["EMPPID"] = flatfile["EMPPID"].astype(int)

        return flatfile.fillna('')


class InputsMergerTask(ExecutionTimeMixin, DataFrameTransformerMixin, Task):
    PARAMETER_CLASS = InputDataCleanerTaskParameters

    def run(self):
        input_data = self._read_input_data(self._data)

        merged_inputs = self._merge_input_data(input_data)

        return [self._dataframe_to_csv(merged_inputs)]

    @classmethod
    def _read_input_data(cls, input_files: []) -> MarketingData:
        adhoc = InputDataParser.parse(input_files[0])
        aims =  InputDataParser.parse(input_files[1])
        list_of_lists = InputDataParser.parse(input_files[2])
        flatfile = InputDataParser.parse(input_files[3])

        return MarketingData(adhoc, aims, list_of_lists, flatfile)

    def _merge_input_data(self, input_data: MarketingData) -> pandas.DataFrame:
        adhoc = input_data.adhoc
        aims = input_data.aims
        list_of_lists = input_data.list_of_lists

        merged_inputs = self._merge_aims(adhoc, aims)
        merged_inputs = self._merge_list_of_lists(merged_inputs, list_of_lists)

        return self._join_listkeys(merged_inputs)

    @classmethod
    def _merge_aims(cls, data: pandas.DataFrame, aims: pandas.DataFrame) -> pandas.DataFrame:
        data = data.dropna(subset=["BEST_EMAIL"])
        aims = aims.dropna(subset=["BEST_EMAIL"])

        return data.merge(aims, left_on='BEST_EMAIL', right_on='BEST_EMAIL', how='left')

    @classmethod
    def _merge_list_of_lists(cls, data, list_of_lists):
        data = data.merge(list_of_lists, left_on='File_Name', right_on='LIST NAME', how='left')

        data = data.drop(columns=column.MERGE_LIST_OF_LISTS_COLUMNS)

        return data.dropna(subset = ["LISTKEY"])

    # pylint: disable= unnecessary-lambda
    @classmethod
    def _join_listkeys(cls, data: pandas.DataFrame):
        joined_listkeys = data.groupby("BEST_EMAIL")['LISTKEY'].apply(lambda x: ''.join(x)).reset_index()

        data = data.merge(joined_listkeys, on="BEST_EMAIL", how='left')

        return data.rename(columns=column.JOIN_LISTKEYS_COLUMNS)


# pylint: disable=redefined-outer-name, protected-access, unused-variable
class FlatfileUpdaterTask(ExecutionTimeMixin, DataFrameTransformerMixin, Task):
    PARAMETER_CLASS = InputDataCleanerTaskParameters

    def run(self):
        contacts, list_of_lists, flatfile, inputs = self._read_input_data(self._data)

        flatfile = self._prune_flatfile_listkeys(flatfile, list_of_lists)

        matched_inputs, unmatched_inputs = self._assign_emppids_to_inputs(inputs, flatfile)

        updated_flatfile = self._update_flatfile_listkeys(flatfile, matched_inputs)

        updated_flatfile = self._add_new_records_to_flatfile(updated_flatfile, unmatched_inputs)

        return [self._dataframe_to_csv(updated_flatfile)]


    @classmethod
    def _read_input_data(cls, input_files: []):
        return [InputDataParser.parse(data) for data in input_files]

    # pylint: disable= cell-var-from-loop
    @classmethod
    def _prune_flatfile_listkeys(cls, flatfile, list_of_lists):
        listkeys_to_remove = list_of_lists[list_of_lists.STATUS.isin(["REPLACE","REMOVE"])].LISTKEY

        for listkey in listkeys_to_remove:
            flatfile.LISTKEY = flatfile.LISTKEY.apply(lambda x: x.replace(listkey, ''))

        return flatfile

    def _assign_emppids_to_inputs(self, inputs, flatfile):
        emails = inputs.BEST_EMAIL.unique()

        new_emails = self._get_new_emails(emails, flatfile)

        matched_inputs = self._assign_emppids_to_known_input(inputs[~inputs.BEST_EMAIL.isin(new_emails)], flatfile)

        unmatched_inputs = self._assign_emppids_to_new_inputs(inputs[inputs.BEST_EMAIL.isin(new_emails)], flatfile)

        return matched_inputs, unmatched_inputs

    @classmethod
    def _update_flatfile_listkeys(cls, flatfile, matched_inputs):
        concatenated_listkeys = cls._concatenate_listkeys_per_best_email(matched_inputs)

        flatfile_first_matching = cls._get_first_matching_records_by_best_email(flatfile, matched_inputs)

        merged_first_matching = cls._merge_new_listkeys_into_flatfile(
            flatfile_first_matching,
            concatenated_listkeys
        )
        flatfile.loc[merged_first_matching.index, "LISTKEY"] = merged_first_matching.LISTKEY

        return flatfile

    @classmethod
    def _add_new_records_to_flatfile(cls, flatfile, unmatched_inputs):
        updated_flatfile = pandas.concat((flatfile, unmatched_inputs), axis=0, ignore_index=True)

        return updated_flatfile.fillna('').drop(columns=["LISTKEY_COMBINED"])

    @classmethod
    def _get_new_emails(cls, emails, flatfile):
        email_data = pandas.DataFrame(data=dict(BEST_EMAIL=emails))

        return email_data[~email_data.BEST_EMAIL.isin(flatfile.BEST_EMAIL)]

    @classmethod
    def _assign_emppids_to_known_input(cls, inputs: pandas.DataFrame, flatfile) -> pandas.DataFrame:
        max_emppid_per_email = flatfile.groupby(flatfile.BEST_EMAIL).EMPPID.max().reset_index()

        return pandas.merge(inputs, max_emppid_per_email, on="BEST_EMAIL", how='left' )

    @classmethod
    def _assign_emppids_to_new_inputs(cls, unmatched_inputs, flatfile):
        last_emppid = max(flatfile["EMPPID"])

        unmatched_inputs.loc[:, "EMPPID"] = range(int(last_emppid)+1, int(last_emppid)+len(unmatched_inputs)+1)

        return unmatched_inputs

    # pylint: disable= unnecessary-lambda
    @classmethod
    def _concatenate_listkeys_per_best_email(cls, matched_inputs):
        return matched_inputs.groupby("BEST_EMAIL")["LISTKEY"].apply(lambda x: "".join(x))

    @classmethod
    def _get_first_matching_records_by_best_email(cls, flatfile, matched_inputs):
        emails = matched_inputs.BEST_EMAIL.unique()

        return flatfile[flatfile.BEST_EMAIL.isin(emails)].drop_duplicates(subset=["BEST_EMAIL"])

    @classmethod
    def _merge_new_listkeys_into_flatfile(cls, flatfile_first_matching, listkeys):
        merged_flatfile = flatfile_first_matching.merge(listkeys, left_on="BEST_EMAIL", right_index=True)

        merged_flatfile["LISTKEY"] = merged_flatfile.LISTKEY_x + merged_flatfile.LISTKEY_y

        merged_flatfile = merged_flatfile.drop(columns=["LISTKEY_x", "LISTKEY_y"])

        return merged_flatfile


@add_schema
@dataclass
class EmailValidatorTaskParameters:
    host: str = None
    account: str = None
    api_key: str = None
    execution_time: str = None
    max_months: int = 0


# pylint: disable=consider-using-with, line-too-long
class EmailValidatorTask(ExecutionTimeMixin, DataFrameTransformerMixin, Task):
    PARAMETER_CLASS = EmailValidatorTaskParameters

    def run(self):
        contacts, flatfile = [InputDataParser.parse(x) for x in self._data]

        dated_flatfile = self._add_last_validated_dates_to_flatfile(flatfile, contacts)

        dated_flatfile['months_since_validated'] = self._calculate_months_since_last_validated(dated_flatfile.last_validated_date)

        validated_flatfile = self._validate_expired_records(dated_flatfile, self._parameters.max_months)

        pruned_flatfile = self._remove_invalid_records(validated_flatfile)

        return [self._dataframe_to_csv(pruned_flatfile)]

    def _add_last_validated_dates_to_flatfile(self, flatfile, contacts):
        data = flatfile.merge(contacts, left_on='EMPPID', right_on='id',how='left')

        if 'last_validated_date' not in data.columns and data is not None:
            data['last_validated_date'] = datetime.strptime(self._parameters.execution_time, '%Y-%m-%d %H:%M:%S')

        return data

    def _calculate_months_since_last_validated(self, column):
        column = pandas.to_datetime(column,format='%m/%d/%Y')
        execution_time = datetime.strptime(self._parameters.execution_time, '%Y-%m-%d %H:%M:%S')

        months_since_last_validated = (execution_time - column).astype('timedelta64[M]')

        return months_since_last_validated

    # pylint: disable=no-member
    def _validate_expired_records(self, dated_flatfile, max_months):
        mask = (dated_flatfile['months_since_validated'] != 'nan') & (dated_flatfile['months_since_validated'] > float(max_months)) & (dated_flatfile['BEST_EMAIL'] != 'nan')

        dated_flatfile['last_validated_date'][mask] =  datetime.strptime(self._parameters.execution_time,'%Y-%m-%d %H:%M:%S')

        expired_dated_flatfile = dated_flatfile[mask]
        email_data_list = list(set(expired_dated_flatfile.BEST_EMAIL.values))

        at_data = AtData(self._parameters.host, self._parameters.account, self._parameters.api_key)

        if len(email_data_list) > 0:
            validated_emails = at_data.validate_emails(email_data_list)

        if validated_emails is not None:
            validated_emails = validated_emails.drop('ID', axis=1)
            dated_flatfile = dated_flatfile.merge(validated_emails, left_on='BEST_EMAIL', right_on='BEST_EMAIL',how='left')

        return dated_flatfile

    @classmethod
    def _remove_invalid_records(cls, validated_flatfile):
        if validated_flatfile is not None:
            validated_flatfile = validated_flatfile[validated_flatfile.FINDING != 'W']
            validated_flatfile = validated_flatfile.drop(columns=column.INVALID_EMAILS_COLUMNS)

        return validated_flatfile


class DuplicatePrunerTask:
    pass


class SFMCPrunerTask:
    pass
