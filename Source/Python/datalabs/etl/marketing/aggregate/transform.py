"""Transformer task for running marketing aggregator"""
from   dataclasses import dataclass
from   datetime import datetime
from bisect import bisect_left
import io
import logging
import os
import pickle
import random
import string

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

        adhoc.BEST_EMAIL = adhoc.BEST_EMAIL.str.lower()

        return adhoc.dropna(subset=["BEST_EMAIL"])

    @classmethod
    def _clean_aims(cls, aims):
        aims = aims.rename(columns=column.AIMS_COLUMNS)[column.AIMS_COLUMNS.values()]

        aims["PHYSICIANFLAG"] = "Y"

        aims.BEST_EMAIL = aims.BEST_EMAIL.str.lower()

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

        flatfile.BEST_EMAIL = flatfile.BEST_EMAIL.str.lower()

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


@add_schema
@dataclass
class FlatfileUpdaterTaskParameters:
    left_merge_key: str
    right_merge_key: str
    execution_time: str = None


# pylint: disable=redefined-outer-name, protected-access, line-too-long
class FlatfileUpdaterTask(ExecutionTimeMixin, DataFrameTransformerMixin, Task):
    PARAMETER_CLASS = FlatfileUpdaterTaskParameters
    MAX_ID_ATTEMPTS = 20

    def run(self):
        contacts, list_of_lists, flatfile, inputs = self._read_input_data(self._data)

        flatfile = self._prune_flatfile_listkeys(flatfile, list_of_lists)

        matched_inputs, unmatched_inputs = self._assign_emppids_to_inputs(inputs, flatfile)

        updated_flatfile = self._update_flatfile_listkeys(flatfile, matched_inputs)

        updated_flatfile = self._add_new_records_to_flatfile(updated_flatfile, unmatched_inputs)

        updated_flatfile = self._assign_new_contactid_to_updated_flatfile(updated_flatfile, contacts)

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

    def _assign_new_contactid_to_updated_flatfile(self, updated_flatfile, contacts):
        old_contact_ids = self._select_contactids_and_empids(contacts)

        merged_flatfile = self._merge_contacts(updated_flatfile, old_contact_ids)

        merged_flatfile = self._insert_contactid_column(merged_flatfile)

        merged_flatfile = self._drop_old_contactid_column(merged_flatfile)

        merged_flatfile = self._rename_columns(merged_flatfile)

        merged_flatfile = self._assign_contactid_to_new_contacts(merged_flatfile)

        merged_flatfile = self._remove_spaces_from_dataframe(merged_flatfile)

        merged_flatfile = self._assign_listkeys_to_updated_flatfile(merged_flatfile)

        return merged_flatfile

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

    @classmethod
    def _select_contactids_and_empids(cls, contacts):
        contact_ids = contacts.loc[:, ['id', 'hs_contact_id']]

        return contact_ids

    def _merge_contacts(self, updated_flatfile, contacts_old_id):
        merged_df = pandas.merge(updated_flatfile.drop(columns=['hs_contact_id']), contacts_old_id, left_on=self._parameters.left_merge_key, right_on=self._parameters.right_merge_key, how='left')

        return merged_df

    @classmethod
    def _insert_contactid_column(cls, merged_df):
        merged_df.insert(1, 'hs_contact_idd', merged_df.hs_contact_id)

        return merged_df

    @classmethod
    def _drop_old_contactid_column(cls, merged_df):
        merged_df = merged_df.drop(columns=['hs_contact_id'])

        return merged_df

    @classmethod
    def _rename_columns(cls, merged_df):
        merged_df.rename(columns={'hs_contact_idd': 'hs_contact_id'}, inplace=True)

        return merged_df

    @classmethod
    def _assign_contactid_to_new_contacts(cls, flatfile):
        id_list = []
        for index in flatfile.index:
            if flatfile['hs_contact_id'][index] != flatfile['hs_contact_id'][index]:
                contact_id = cls._generate_unique_contact_id(id_list, flatfile['hs_contact_id'])
                flatfile['hs_contact_id'][index] = contact_id

        return flatfile

    @classmethod
    def _remove_spaces_from_dataframe(cls, merged_df):
        merged_df = merged_df.apply(lambda x: x.str.strip())

        return merged_df

    #@classmethod
    def _assign_listkeys_to_updated_flatfile(self, merged_df):
        duplicated_merged_df = self._get_contacts_with_duplicate_emails(merged_df)

        listkey_df = self._get_listkeys_for_contacts_with_same_emails(duplicated_merged_df)

        merged_df = self._remove_duplicate_contacts(merged_df, duplicated_merged_df, listkey_df)

        merged_df = self._assign_liskeys(merged_df, listkey_df)

        return merged_df

    @classmethod
    def _generate_unique_contact_id(cls, id_list, existing_ids):
        found_contact_id = False
        contact_id = None
        attempts = 0

        while not found_contact_id and attempts <= cls.MAX_ID_ATTEMPTS:
            contact_id = cls._generate_contact_id()
            found_contact_id = cls._is_contact_id_unique(id_list, contact_id, existing_ids)
            attempts += 1

        if attempts > cls.MAX_ID_ATTEMPTS:
            raise ValueError(
                f'The maximum number of attempts ({cls.MAX_ID_ATTEMPTS}) to '
                f'generate a new, unique contact ID was exceeded.',
            )

        return contact_id

    @classmethod
    def _generate_contact_id(cls, size=15, chars=None):
        if not chars:
            chars = string.ascii_uppercase + string.ascii_lowercase + string.digits

        return ''.join(random.choice(chars) for _ in range(size))

    @classmethod
    def _is_contact_id_unique(cls, id_list, contact_id, existing_ids):
        index = bisect_left(id_list, contact_id)
        found_contact_id = False

        if not (index != len(id_list) and id_list[index] == contact_id) and (contact_id not in existing_ids):
            found_contact_id = True

        return found_contact_id

    @classmethod
    def _get_contacts_with_duplicate_emails(cls, flatfile):
        return flatfile[flatfile.duplicated('BEST_EMAIL') | flatfile.duplicated('BEST_EMAIL', keep='last')]

    @classmethod
    def _get_listkeys_for_contacts_with_same_emails(cls, duplicated_flatfile):
        duplicated_sorted = duplicated_flatfile.sort_values(by=['NAME'], ascending= False)

        duplicated_dict = duplicated_sorted.to_dict('records')

        best_emails, dict_list = [], []

        for row in duplicated_dict:
            if row['BEST_EMAIL'] not in best_emails:
                row_data = duplicated_sorted[duplicated_sorted['BEST_EMAIL'] == row['BEST_EMAIL']].copy()
                values= row_data['LISTKEY'].to_list()
                values = [x for x in values if str(x) != 'nan']
                values = list(set(values))
                values = ''.join(values)
                row_data.iloc[0]['LISTKEY'] = values
                dict_list.append(row_data.iloc[0])
                best_emails.append(row['BEST_EMAIL'])

        return pandas.DataFrame(dict_list)

    @classmethod
    def _remove_duplicate_contacts(cls, flatfile, duplicated_flatfile, listkey_df):
        duplicated = duplicated_flatfile[~duplicated_flatfile['hs_contact_id'].isin(listkey_df['hs_contact_id'])]

        return flatfile[~flatfile['hs_contact_id'].isin(duplicated['hs_contact_id'])]

    @classmethod
    def _assign_liskeys(cls, flatfile, listkey_df):
        listkey_dict = listkey_df.to_dict('records')
        for row in listkey_dict:
            idx = flatfile.index[flatfile['hs_contact_id'] == row['hs_contact_id']]
            flatfile.loc[idx,'LISTKEY'] = row['LISTKEY']

        return flatfile


@add_schema
@dataclass
class EmailValidatorTaskParameters:
    host: str
    account: str
    api_key: str
    execution_time: str
    max_months: int
    left_merge_key: str
    right_merge_key: str

# pylint: disable=consider-using-with, line-too-long
class EmailValidatorTask(ExecutionTimeMixin, DataFrameTransformerMixin, Task):
    PARAMETER_CLASS = EmailValidatorTaskParameters

    def run(self):
        dataset_with_emails, dataset_with_validation_dates = [InputDataParser.parse(x) for x in self._data]

        dated_dataset_with_emails = self._add_existing_validation_dates_to_emails(dataset_with_emails, dataset_with_validation_dates)

        dated_dataset_with_emails = self._calculate_months_since_last_validated(dated_dataset_with_emails)

        dated_dataset_with_emails = self._validate_expired_records(dated_dataset_with_emails)

        return [self._dataframe_to_csv(dated_dataset_with_emails)]

    def _add_existing_validation_dates_to_emails(self, dataset_with_emails, dataset_with_validation_dates):
        if not dataset_with_validation_dates[self._parameters.right_merge_key].is_unique:
            dataset_with_validation_dates = self._remove_duplicate_dataset_with_validation_dates(dataset_with_validation_dates)

        data = dataset_with_emails.merge(dataset_with_validation_dates, left_on=self._parameters.left_merge_key, right_on=self._parameters.right_merge_key, how='left')

        data['email_last_validated'] = data.groupby(['BEST_EMAIL'], sort=False)['email_last_validated'].apply(lambda x: x.ffill())

        return data

    def _calculate_months_since_last_validated(self, dated_dataset_with_emails):
        execution_time = datetime.strptime(self._parameters.execution_time, '%Y-%m-%d %H:%M:%S')

        dated_dataset_with_emails["months_since_validated"] = (execution_time - pandas.to_datetime(dated_dataset_with_emails.email_last_validated[~dated_dataset_with_emails.email_last_validated.isnull()])).astype('timedelta64[M]')

        dated_dataset_with_emails.months_since_validated[dated_dataset_with_emails.email_last_validated.isnull()] = 6

        return dated_dataset_with_emails

    # pylint: disable=no-member, no-value-for-parameter
    def _validate_expired_records(self, dated_dataset_with_emails):
        dated_dataset_with_emails = self._unset_update_flag_for_unexpired_emails(dated_dataset_with_emails)

        email_data_list = self._get_expired_emails(dated_dataset_with_emails)

        validated_emails = self._validate_emails(email_data_list)

        dated_dataset_with_emails = self._set_update_flag_for_valid_emails(dated_dataset_with_emails, validated_emails)

        dated_dataset_with_emails = self._remove_invalid_records(dated_dataset_with_emails)

        dated_dataset_with_emails = self._update_email_last_validated(dated_dataset_with_emails)

        return dated_dataset_with_emails

    @classmethod
    def _remove_duplicate_dataset_with_validation_dates(cls, dataset_with_validation_dates):
        return dataset_with_validation_dates[['BEST_EMAIL', 'email_last_validated']].drop_duplicates()

    def _unset_update_flag_for_unexpired_emails(self, dated_dataset_with_emails):
        mask =  dated_dataset_with_emails.months_since_validated < int(self._parameters.max_months)

        dated_dataset_with_emails.loc[mask, 'update'] = False

        dated_dataset_with_emails.loc[(~mask & ~dated_dataset_with_emails.BEST_EMAIL.isnull()), 'update'] = True

        return dated_dataset_with_emails

    # pylint: disable=singleton-comparison
    @classmethod
    def _get_expired_emails(cls, dated_dataset_with_emails):
        expired_emails = list(set(dated_dataset_with_emails[dated_dataset_with_emails['update'] == True].BEST_EMAIL.values))

        return expired_emails

    def _validate_emails(self, email_data_list):
        at_data = AtData(self._parameters.host, self._parameters.account, self._parameters.api_key)

        validated_emails = at_data.validate_emails(email_data_list)

        return validated_emails

    @classmethod
    def _set_update_flag_for_valid_emails(cls, dated_dataset_with_emails, validated_emails):
        dated_dataset_with_emails.loc[dated_dataset_with_emails.BEST_EMAIL.isin(validated_emails), 'update'] = True

        return dated_dataset_with_emails

    @classmethod
    def _remove_invalid_records(cls, dated_dataset_with_emails):
        return dated_dataset_with_emails[~dated_dataset_with_emails['update'].isnull()]

    # pylint: disable=singleton-comparison
    def _update_email_last_validated(self, dated_dataset_with_emails):
        dated_dataset_with_emails.loc[ dated_dataset_with_emails['update'] == True, 'email_last_validated'] = datetime.strptime(self._parameters.execution_time,'%Y-%m-%d %H:%M:%S').strftime("%m/%d/%Y")

        return dated_dataset_with_emails


class SFMCPrunerTask(ExecutionTimeMixin, DataFrameTransformerMixin, Task):
    Parameter_class = InputDataCleanerTaskParameters

    def run(self):
        input_data = [InputDataParser.parse(x) for x in self._data][0]

        updated_contacts = input_data[['id', 'hs_contact_id', 'email_last_validated']][~input_data.id.isnull()]

        return [self._dataframe_to_csv(updated_contacts)]


class DuplicatePrunerTask:
    pass
