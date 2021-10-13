""" Address load file aggregation class for combining output of several address-load-file-generating processes """
from datetime import datetime
from glob import glob
import logging
import os
import shutil
from string import digits, ascii_uppercase
import pandas as pd
# pylint: disable=unused-import
import settings


logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel('INFO')


# address load files MUST HAVE THESE COLUMNS (but values for some are optional)
REQUIRED_COLUMNS = [
    'entity_id', 'me#', 'comm_id', 'usage', 'load_type_ind', 'addr_type',
    'addr_line_1', 'addr_line_2', 'addr_line_3', 'addr_city', 'addr_state',
    'addr_zip', 'addr_plus4', 'addr_country', 'source', 'source_dtm'
]
# subset of required columns which MUST have values -- NON-OPTIONAL
REQUIRED_NON_NULL_COLUMNS = [
    'usage', 'load_type_ind', 'addr_type', 'addr_line_1', 'addr_city',
    'addr_state', 'addr_zip', 'source', 'source_dtm'
]


# pylint: disable=logging-fstring-interpolation, bare-except
class AddressBatchLoadAggregator:
    def __init__(self):
        self.process_directories = os.environ.get('BATCHLOAD_PROCESS_DIRECTORIES').split(',')
        self.save_directory = os.environ.get('ADDRESS_LOAD_SAVE_DIR')
        self.error_directory = os.environ.get('ADDRESS_LOAD_ERRORS_DIR')
        self.directory_staging_file_dict = {}  # {'dir1': ['C:/path/to/dir1/file1', 'C:/path/to/dir1/file2']}
        self.files = []

    def run(self):
        self._validate_process_directories()
        valid_dataframe_list = []
        valid_component_file_list = []
        invalid_dataframe_list = []
        invalid_component_file_list = []
        self.files = self._get_staging_files()
        for file in self.files:
            valid_data, invalid_data = self._process_component_file(path_to_file=file)

            if valid_data is not None:
                valid_dataframe_list.append(valid_data)
                valid_component_file_list.append(file)
            else:
                invalid_component_file_list.append(file)

            if invalid_data is not None:
                invalid_dataframe_list.append(invalid_data)

        LOGGER.info(f'VALID COMPONENT FILES: {str(valid_component_file_list)}')
        LOGGER.info(f'INVALID COMPONENT FILES: {str(invalid_component_file_list)}')
        data = pd.concat(valid_dataframe_list, ignore_index=True)
        valid_aggregate_data, invalid_aggregate_data = self._process_aggregate_data(aggregate_data=data)

        self._save_invalid_data(invalid_data=invalid_aggregate_data, component_files=invalid_component_file_list)
        self._save_valid_data(data=valid_aggregate_data)

    def _validate_process_directories(self):
        for directory in self.process_directories:
            if not os.path.exists(directory):
                raise FileNotFoundError(f'Process directory "{directory}" not found.')
        if not os.path.exists(self.save_directory):
            raise FileNotFoundError(f'Address batch load save directory "{self.save_directory}" not found.')
        if not os.path.exists(self.error_directory):
            raise FileNotFoundError(f'Address batch load save directory "{self.error_directory}" not found.')

    def _get_staging_files(self):
        files = []
        for directory in self.process_directories:
            directory_files = self._get_staging_files_from_directory(directory)
            files.extend(directory_files)

            self.directory_staging_file_dict[directory] = directory_files

        for file in files:
            LOGGER.info(f'FOUND COMPONENT FILE - {file}')
        return files

    def _process_component_file(self, path_to_file: str):
        this_file_data = pd.read_csv(path_to_file, dtype=str)
        for col in this_file_data.columns.values:
            this_file_data[col] = this_file_data[col].astype(str).apply(lambda x: x.strip())

        is_valid_structure = self._is_valid_component_file_structure(this_file_data)
        LOGGER.info(f" - VALID STRUCTURE - {path_to_file} - {is_valid_structure}")

        this_file_data['filename'] = path_to_file.replace('\\', '/').split('/')[-1]

        if not is_valid_structure:
            valid_data = None
            invalid_data = this_file_data
        else:
            valid_data = self._get_valid_rows(this_file_data)
            # invalid_data is data with erroneous row data, found where entity or ME # not found in filtered valid data
            invalid_data = this_file_data[
                (~this_file_data['me#'].isin(valid_data['me#'])) |
                (~this_file_data['entity_id'].isin(valid_data['entity_id']))
            ]
        return valid_data, invalid_data

    @classmethod
    def _process_aggregate_data(cls, aggregate_data: pd.DataFrame):
        """
        Would be inaccurate/redundant to set multiple addresses with the same usage to a single physician,
        so this function identifies which records are unique by (individual, usage) and which are not.
        """
        data = aggregate_data.copy().drop(columns=['filename'], axis=1).drop_duplicates()
        me_counts = data.groupby(by=['me#', 'usage']).size()
        entity_counts = data.groupby(by=['entity_id', 'usage']).size()

        multiples_me = me_counts[me_counts > 1]
        multiples_entity_id = entity_counts[entity_counts > 1]

        reindexed_me = data.set_index(['me#', 'usage'])
        reindexed_entity_id = data.set_index(['entity_id', 'usage'])

        # valid_data is data where the me+usage key or entity_id+usage key is unique
        valid_data = pd.concat(
            [
                reindexed_me[~reindexed_me.index.isin(multiples_me.index)].reset_index(),
                reindexed_entity_id[~reindexed_entity_id.index.isin(multiples_entity_id.index)].reset_index()
            ],
            ignore_index=True
        ).drop_duplicates()

        invalid_data = pd.concat(
            [
                reindexed_me[reindexed_me.index.isin(multiples_me.index)].reset_index(),
                reindexed_entity_id[reindexed_entity_id.index.isin(multiples_entity_id.index)].reset_index()
            ],
            ignore_index=True
        ).drop_duplicates()

        LOGGER.info(f"AGGREGATE DATA - VALID: {str(len(valid_data))}\t\tINVALID: {str(len(invalid_data))}")

        return valid_data, invalid_data

    def _save_invalid_data(self, invalid_data: pd.DataFrame, component_files: list):
        invalid_data = self._reorder_batch_load_column_order(invalid_data).replace('nan', '')

        LOGGER.info('SAVING INVALID DATA')
        error_directory = self.error_directory + f'/{str(datetime.now().date())}'

        if not os.path.exists(error_directory):
            os.mkdir(error_directory)

        invalid_data_target_path = error_directory + '/invalid_aggregate_data.csv'
        invalid_data.to_csv(invalid_data_target_path, index=False)

        invalid_component_file_target_path = error_directory + '/invalid_component_file_list.txt'
        with open(invalid_component_file_target_path, 'w') as file:
            file.writelines(component_files)

    def _save_valid_data(self, data):
        data = self._reorder_batch_load_column_order(data).replace('nan', '')
        LOGGER.info('SAVING FINALIZED AGGREGATE VALID DATA')
        if 'filename' in data.columns.values:
            data.drop(columns=['filename'], axis=1, inplace=True)

        target_path = self.save_directory + '/address_load.csv'
        if not os.path.exists(self.save_directory + '/archive'):
            os.mkdir(self.save_directory + '/archive')

        target_archive_path = self.save_directory + f'/archive/address_load_{str(datetime.now().date())}.csv'
        data.to_csv(target_archive_path, index=False)
        data.to_csv(target_path, index=False)

    @classmethod
    def _get_staging_files_from_directory(cls, directory):
        return glob(directory + '/address_load*.csv')

    def _move_staging_files_to_archive(self):
        for directory in self.directory_staging_file_dict:
            archive_directory = directory + '/archive'
            if not os.path.exists(archive_directory):
                os.mkdir(archive_directory)
            for file in self.directory_staging_file_dict[directory]:
                filename = file.replace('\\', '/').split('/')[-1]
                filename = self._insert_datestamp(filename)

                target_path = archive_directory + f'/{filename}'
                try:
                    shutil.copy2(file, target_path)
                except:
                    pass  # perhaps cannot overwrite existing file

    @classmethod
    def _insert_datestamp(cls, filename):
        tokens = filename.split('.')
        name = '.'.join(tokens[:-1])
        filetype = tokens[-1]
        name += f'_{str(datetime.now().date())}'
        return '.'.join([name, filetype])

    @classmethod
    def _is_valid_component_file_structure(cls, data: pd.DataFrame):
        # required columns are hard-coded
        is_valid = True
        columns = data.columns.values
        missing_columns = []
        for col in REQUIRED_COLUMNS:
            if col not in columns:
                is_valid = False  # required column not found in dataframe
                missing_columns.append(col)
        if len(missing_columns) > 0:
            LOGGER.info(f"MISSING COLUMNS: {str(missing_columns)}")
        if len(columns) > len(REQUIRED_COLUMNS):
            LOGGER.info(f"REQUIRED COLUMNS: {str(REQUIRED_COLUMNS)}")
            LOGGER.info(f"FOUND COLUMNS: {str(columns)}")
            is_valid = False  # more columns found than required
        return is_valid

    def _get_valid_rows(self, data):
        valid_data = data.copy()
        valid_data = valid_data[valid_data['usage'].apply(self._is_valid_usage)]
        valid_data = valid_data[valid_data['addr_zip'].apply(self._is_valid_zip)]
        valid_data = valid_data[valid_data['load_type_ind'].apply(self._is_valid_load_type_ind)]
        valid_data = valid_data[valid_data['addr_state'].apply(self._is_valid_state)]
        valid_data = valid_data[valid_data['source_dtm'].apply(self._is_valid_date)]
        valid_data = valid_data[valid_data['addr_type'].apply(self._is_valid_addr_type)]

        valid_rows = []
        for _, row in valid_data.iterrows():
            is_valid_row = self._is_valid_row(row)

            if is_valid_row:
                valid_rows.append(row)
        valid_data = pd.concat(valid_rows, ignore_index=True, axis=1).T
        valid_data['source_dtm'] = pd.to_datetime(valid_data['source_dtm'])
        return valid_data

    def _is_valid_row(self, row):
        is_valid_row = True
        # entity_id OR me# must exist
        if self._isna(row['entity_id']) and self._isna(row['me#']):
            is_valid_row = False

        for col in REQUIRED_NON_NULL_COLUMNS:
            if self._isna(row[col]):
                is_valid_row = False  # column exists in file but has a null value
        return is_valid_row

    @classmethod
    def _isna(cls, text):
        return text in [None, '', 'nan', 'null', 'none', '.', '-']

    @classmethod
    def _is_valid_entity_id(cls, val):
        try:
            return str(val).isdigit()
        except:
            return False

    @classmethod
    def _is_valid_me_number(cls, val):
        try:
            return len(val) == 11 and isinstance(val, str) and all(x.isdigit() for x in val)
        except:
            return False

    @classmethod
    def _is_valid_usage(cls, val):
        try:
            return val in ['PP', 'PO']
        except:
            return False

    @classmethod
    def _is_valid_zip(cls, val):
        try:
            return len(str(val)) in (4, 5) and all(str(x) in digits for x in val)
        except:
            return False

    @classmethod
    def _is_valid_load_type_ind(cls, val):
        try:
            return val in ('R', 'A', 'D')
        except:
            return False

    @classmethod
    def _is_valid_state(cls, val):
        try:
            return isinstance(val, str) and len(val) == 2 and all(x in ascii_uppercase for x in val)
        except:
            return False

    # pylint: disable=unused-argument
    @classmethod
    def _is_valid_addr_type(cls, val):
        try:
            # return val in ('N', 'OF', 'HO', 'H', 'GROUP')  # unsure about rules, figure out later
            return True
        except:
            return False

    @classmethod
    def _is_valid_date(cls, val):
        try:
            if not isinstance(val, datetime):
                pd.to_datetime(val)  # should be able to cast
            return True
        except:
            return False

    @classmethod
    def _reorder_batch_load_column_order(cls, data: pd.DataFrame):
        batch_data = pd.DataFrame()
        for col in REQUIRED_COLUMNS:
            batch_data[col] = data[col]
        return batch_data
