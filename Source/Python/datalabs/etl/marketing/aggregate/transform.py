"""Transformer task for running marketing aggregator"""
from   dataclasses import dataclass
from   datetime import datetime
import io
import logging
import os
import pickle
import random
import string

from   dateutil.parser import parse
import pandas
import numpy as np

from   datalabs.access.atdata import AtData
from   datalabs.etl.csv import CSVReaderMixin, CSVWriterMixin
from   datalabs.etl.marketing.aggregate import column
from   datalabs.etl.task import ExecutionTimeMixin
from   datalabs.parameter import add_schema
from   datalabs.task import Task, TaskException

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
class SourceFileListTransformerParameters:
    execution_time: str = None


class SourceFileListTransformerTask(ExecutionTimeMixin, CSVReaderMixin, CSVWriterMixin, Task):
    PARAMETER_CLASS = SourceFileListTransformerParameters

    def run(self):
        adhoc_list_of_lists, aims, flatfile = [
                                              self._csv_to_dataframe(x, sep='\r\n', header=None, index_col=None)
                                              for x in self._data
                                          ]

        execution_month = datetime.strptime(self._parameters.execution_time, '%Y-%m-%dT%H:%M:%S').month
        file_lists = []

        file_lists.append(self._extract_adhoc_paths(adhoc_list_of_lists))

        file_lists.append(self._extract_datestamped_path(aims, execution_month))

        file_lists.append(self._extract_list_of_lists_path(adhoc_list_of_lists))

        file_lists.append(self._extract_datestamped_path(flatfile, execution_month))

        return [self._dataframe_to_csv(data, header=False) for data in file_lists]

    @classmethod
    def _extract_adhoc_paths(cls, paths):
        return paths[~paths.iloc[:,0].str.contains('List of Lists')]

    @classmethod
    def _extract_list_of_lists_path(cls, paths):
        return paths[paths.iloc[:,0].str.contains('List of Lists')]

    @classmethod
    def _extract_datestamped_path(cls, paths, execution_month):
        if len(paths) == 0:
            raise ValueError(f"No path loaded from file {paths}")

        return paths[paths.iloc[:,0].apply(
                   lambda x: parse(x, fuzzy=True).month
               ).astype(str).str.contains(str(execution_month))].iloc[[-1]]


@add_schema
@dataclass
class InputDataCleanerTaskParameters:
    execution_time: str = None


class InputDataCleanerTask(ExecutionTimeMixin, CSVReaderMixin, CSVWriterMixin, Task):
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

        adhoc.File_Name = adhoc["File_Name"].apply(lambda x: os.path.splitext(x)[0])

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


class InputsMergerTask(ExecutionTimeMixin, CSVReaderMixin, CSVWriterMixin, Task):
    PARAMETER_CLASS = InputDataCleanerTaskParameters

    def run(self):
        input_data = self._read_input_data(self._data)

        merged_inputs = self._merge_input_data(input_data)

        return [self._dataframe_to_csv(merged_inputs)]

    @classmethod
    def _read_input_data(cls, input_files: []) -> MarketingData:
        adhoc = InputDataParser.parse(input_files[0])
        aims =  InputDataParser.parse(input_files[1])
        flatfile = InputDataParser.parse(input_files[2])
        list_of_lists = InputDataParser.parse(input_files[3])

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
    def _merge_list_of_lists(cls, data, list_of_lists) -> pandas.DataFrame:
        data = data.merge(list_of_lists, left_on='File_Name', right_on='LIST NAME', how='left')

        data = data.drop(columns=column.MERGE_LIST_OF_LISTS_COLUMNS)

        return data.dropna(subset = ["LISTKEY"])

    # pylint: disable= unnecessary-lambda
    @classmethod
    def _join_listkeys(cls, data: pandas.DataFrame):
        joined_listkeys = data.groupby("BEST_EMAIL")['LISTKEY'].apply(lambda x: ''.join(x)).reset_index()

        data = data.merge(joined_listkeys, on="BEST_EMAIL", how='left')

        return data.rename(columns=column.JOIN_LISTKEYS_COLUMNS)


# pylint: disable=redefined-outer-name, protected-access, line-too-long
class FlatfileUpdaterTask(ExecutionTimeMixin, CSVReaderMixin, CSVWriterMixin, Task):
    MAX_ID_ATTEMPTS = 20

    def run(self):
        contacts, list_of_lists, flatfile, inputs = self._read_input_data(self._data)

        flatfile = self._prune_flatfile_listkeys(flatfile, list_of_lists)

        matched_inputs, unmatched_inputs = self._assign_emppids_to_inputs(inputs, flatfile)

        flatfile = self._add_new_records_to_flatfile(flatfile, unmatched_inputs)

        flatfile = self._update_flatfile_listkeys(flatfile, matched_inputs)

        flatfile = self._assign_new_contact_ids_to_flatfile(flatfile, contacts)

        return [self._dataframe_to_csv(flatfile)]

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

        new_emails = self._get_new_emails(emails, flatfile).BEST_EMAIL

        matched_inputs = self._assign_emppids_to_known_inputs(inputs, new_emails, flatfile)

        unmatched_inputs = self._assign_emppids_to_new_inputs(inputs, new_emails, flatfile)

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
    def _assign_new_contact_ids_to_flatfile(cls, flatfile, contacts):
        merged_flatfile = cls._merge_contacts(flatfile, contacts)

        merged_flatfile = cls._reposition_contact_id_column(merged_flatfile)

        duplicated_merged_df = cls._get_contacts_with_duplicate_emails(merged_flatfile)

        listkey_df = cls._get_listkeys_for_contacts_with_same_emails(duplicated_merged_df)

        merged_flatfile = cls._remove_duplicate_contacts(merged_flatfile, duplicated_merged_df, listkey_df)

        merged_flatfile = cls._assign_contact_ids_to_new_contacts(merged_flatfile)

        return merged_flatfile

    @classmethod
    def _get_new_emails(cls, emails, flatfile):
        email_data = pandas.DataFrame(data=dict(BEST_EMAIL=emails))

        return email_data[~email_data.BEST_EMAIL.isin(flatfile.BEST_EMAIL)]

    @classmethod
    def _assign_emppids_to_known_inputs(cls, inputs: pandas.DataFrame,new_emails, flatfile) -> pandas.DataFrame:
        known_inputs = inputs.loc[~inputs.BEST_EMAIL.isin(new_emails), :].copy()
        max_emppid_per_email = flatfile.groupby(flatfile.BEST_EMAIL).EMPPID.max().reset_index()

        return pandas.merge(known_inputs, max_emppid_per_email, on="BEST_EMAIL", how='left' )

    @classmethod
    def _assign_emppids_to_new_inputs(cls, inputs, new_emails, flatfile):
        new_inputs = inputs.loc[inputs.BEST_EMAIL.isin(new_emails), :].copy()
        last_emppid = max(flatfile["EMPPID"])
        new_emppids = list(range(int(last_emppid)+1, int(last_emppid)+ len(new_inputs)+1))

        new_inputs["EMPPID"] = new_emppids

        return new_inputs

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
    def _merge_contacts(cls, flatfile, contacts):
        contact_ids = contacts.loc[:, ['id', 'hs_contact_id']]

        flatfile = pandas.merge(flatfile, contact_ids, left_on='id', right_on='id', how='left', suffixes=('', '_y'))

        flatfile.drop(flatfile.filter(regex='_y$').columns, axis=1, inplace=True)

        return flatfile

    @classmethod
    def _reposition_contact_id_column(cls, flatfile):
        flatfile.insert(1, 'hs_contact_idd', flatfile.hs_contact_id)

        flatfile = flatfile.drop(columns=['hs_contact_id'])

        flatfile.rename(columns={'hs_contact_idd': 'hs_contact_id'}, inplace=True)

        return flatfile

    # pylint: disable=anomalous-backslash-in-string
    @classmethod
    def _assign_contact_ids_to_new_contacts(cls, flatfile):
        flatfile.hs_contact_id = flatfile.hs_contact_id.replace(["^\s*$"], np.NaN, regex=True)

        new_record_count = len(flatfile[flatfile.hs_contact_id.isna()])

        contact_ids = cls._generate_unique_contact_ids(new_record_count, flatfile['hs_contact_id'])

        if len(contact_ids) > 0:
            flatfile.loc[flatfile.hs_contact_id.isna(), "hs_contact_id"] = contact_ids

        return flatfile

    # pylint: disable=comparison-with-itself
    @classmethod
    def _generate_unique_contact_ids(cls, count, existing_contact_ids):
        existing_contact_ids = set(ids for ids in existing_contact_ids.unique() if ids == ids)
        unique_contact_ids = existing_contact_ids.copy()
        start_count = len(unique_contact_ids)
        current_count = start_count
        iterations = 0

        while (current_count - start_count) < count:
            unique_contact_ids.add(cls._generate_contact_id())

            new_count = len(unique_contact_ids)

            if new_count > current_count:
                iterations = 0
            else:
                iterations += 1

            if iterations > cls.MAX_ID_ATTEMPTS:
                raise TaskException("Exceeded max Contact ID generation attempts.")

            current_count = new_count

        return list(unique_contact_ids.difference(existing_contact_ids))

    @classmethod
    def _generate_contact_id(cls, size=15, chars=None):
        if not chars:
            chars = string.ascii_uppercase + string.ascii_lowercase + string.digits

        return ''.join(random.choice(chars) for _ in range(size))

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
class EmailValidatorTask(ExecutionTimeMixin, CSVReaderMixin, CSVWriterMixin, Task):
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


class SFMCPrunerTask(ExecutionTimeMixin, CSVReaderMixin, CSVWriterMixin, Task):
    Parameter_class = InputDataCleanerTaskParameters

    def run(self):
        input_data = [InputDataParser.parse(x) for x in self._data][0]

        updated_contacts = input_data[['id', 'hs_contact_id', 'email_last_validated']][~input_data.id.isnull()]

        return [self._dataframe_to_csv(updated_contacts)]


class DuplicatePrunerTask:
    pass
