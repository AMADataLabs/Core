""" Dear God what is this """
# pylint: disable=no-name-in-module,import-error,wildcard-import,undefined-variable,protected-access,unused-import,too-many-instance-attributes,logging-fstring-interpolation,unnecessary-lambda,abstract-class-instantiated,logging-format-interpolation,no-member,trailing-newlines,trailing-whitespace,consider-using-from-import,function-redefined,use-a-generator,f-string-without-interpolation,invalid-name,bare-except,unnecessary-comprehension,unused-variable,consider-using-dict-items

from dataclasses import dataclass
from datetime import datetime
import logging
import os
from sqlite3 import Connection

from dateutil.relativedelta import relativedelta
import pandas as pd

from datalabs.analysis.vertical_trail.physician_contact.column_definitions import *
import settings


LOGGER = logging.Logger(__name__)
LOGGER.setLevel(logging.INFO)


@dataclass
class ExpectedFileColumns:
    results = FILE_RESULT_COLUMNS
    samples = FILE_SAMPLE_COLUMNS
    dict = {
        'vertical_trail_results': results,
        'vertical_trail_samples': samples
    }


@dataclass
class TableColumns:
    results = TABLE_RESULTS_COLUMNS
    samples = TABLE_SAMPLE_COLUMNS
    dict = {
            'vertical_trail_results': results,
            'vertical_trail_samples': samples
    }


class VTPhysicianContactArchive:
    def __init__(self, database_path=None):
        self._database_path = database_path
        self.connection = None
        if self._database_path is not None:
            self.connection = Connection(database_path)

        # column names of tables in database
        self.table_columns = TableColumns()

        # column names of Excel files of samples sent to and results received from Vertical Trail
        self.expected_file_columns = ExpectedFileColumns()

        self._batch_load_save_dir = None

    def get_latest_sample_id(self):
        sql = "SELECT MAX(sample_id) FROM vertical_trail_samples;"
        result = self.connection.execute(sql).fetchone()[0]
        LOGGER.info(f'Latest existing sample_id: {result}')
        return result

    def get_latest_results_sample_id(self):
        sql = "SELECT MAX(sample_id) FROM vertical_trail_results;"
        result = self.connection.execute(sql).fetchone()[0]
        LOGGER.info(f'Latest existing sample_id of results: {result}')
        return result

    def get_vt_sample_data_past_n_months(self, n, as_of_date=datetime.now().date()):
        sql = """SELECT * FROM vertical_trail_samples"""
        data = pd.read_sql(sql=sql, con=self.connection)

        data['sample_date'] = pd.to_datetime(data['sample_date'])
        data['sample_date'] = data['sample_date'].apply(lambda x: x.date())

        data['month_diff'] = [relativedelta(as_of_date, sample_date) for sample_date in data['sample_date'].values]
        data['month_diff'] = data['month_diff'].apply(lambda x: x.months)

        data = data[data['month_diff'] <= int(n)]

        del data['month_diff']

        return data

    def ingest_sample_file(self, file_path: str):
        LOGGER.info(f'Ingesting sample file located at: {file_path}')
        data = pd.read_excel(file_path, dtype=str)
        LOGGER.info(f'Sample data records: {len(data)}')
        self.ingest_sample_data(data)

    def ingest_sample_data(self, data: pd.DataFrame):
        data.fillna('', inplace=True)

        for i, r in data.iterrows():
            self.insert_row(table='vertical_trail_samples', vals=[v for v in r.values])
        self.connection.commit()

    def ingest_result_file(self, file_path: str):
        LOGGER.info(f'Ingesting result file at: {file_path}')
        data = pd.read_csv(file_path, dtype=str)
        data = data[
            ['SAMPLE_ID',
             'ROW_ID',
             'OFFICE 1 PHONE NUMBER - GENERAL',
             'OFFICE 1 FAX NUMBER',
             'OFFICE 1 EMAIL',
             'Notes for AMA'
             ]
        ]
        LOGGER.info(f'Result data records: {len(data)}')
        self.ingest_result_data(data=data)

        # If ingesting the results immediately on return, we can simply integrate the batch file creation with ingestion
        sample_id = data['SAMPLE_ID'].drop_duplicates().values[0]
        self.create_batch_load_file(sample_id=sample_id)

    def ingest_result_data(self, data: pd.DataFrame):
        data.fillna('', inplace=True)

        for i, r in data.iterrows():
            self.insert_row(table='vertical_trail_results', vals=[v for v in r.values])
        self.connection.commit()

    def insert_row(self, table, vals):
        cols = self.table_columns.dict[table]

        sql = "INSERT INTO {}({}) VALUES({});".format(
            table,
            ','.join(cols),
            ','.join(['"' + str(v) + '"' for v in vals])
        )
        try:
            self.connection.execute(sql)
        except:
            print(sql)

    def get_results_for_sample_ids(self, sample_ids):
        results = []
        if not isinstance(sample_ids, (list, set)):
            sample_ids = [sample_ids]

        for sample_id in sample_ids:
            data = self.get_results_for_sample_id(sample_id)
            results.append(data)

        return pd.concat(results)

    def get_results_for_sample_id(self, sample_id: int):
        sql = f"SELECT * FROM " +\
              f"vertical_trail_samples s INNER JOIN vertical_trail_results r " +\
              f"ON (s.sample_id = r.sample_id AND s.row_id = r.row_id) " +\
              f"WHERE s.sample_id = {sample_id}"

        data = pd.read_sql(sql=sql, con=self.connection)
        return data

    def insert_humach_sample_reference(self, humach_sample_id, other_sample_id, other_sample_source):
        sql = f"INSERT INTO sample_reference(humach_sample_id, other_sample_id, other_sample_source) " + \
              f"VALUES ({humach_sample_id}, {other_sample_id}, '{other_sample_source}')"
        LOGGER.info(f'Created reference sample record -- Humach: {humach_sample_id} -- Other: {other_sample_id}')
        self.connection.execute(sql)
        self.connection.commit()

    def create_batch_load_file(self, sample_id=None):
        LOGGER.info(f'Creating IT Batch Load file for sample_id: {sample_id}')
        if sample_id is None:
            sample_id = self.get_latest_results_sample_id()

        # load results for sample ID
        sql = \
            f"""
            SELECT 
                s.sample_id,
                s.row_id,
                s.me,
                r.phone_number
            FROM
                vertical_trail_samples s
                INNER JOIN
                vertical_trail_results r
                ON (r.sample_id = s.sample_id AND r.row_id = s.row_id)
            WHERE
                s.sample_id = {sample_id}
            """.strip()
        data = pd.read_sql(con=self.connection, sql=sql)

        # filter to valid phone results
        data = data[data['phone_number'].notna()]
        data = data[data['phone_number'] != 'None']

        # format data
        batchload_data = pd.DataFrame()

        batchload_file_date = str(datetime.now().date())
        # batchload_cols = ['me', 'phone_number', 'fax', 'source', 'verified_date', 'load_type']

        batchload_data['me'] = data['me']
        batchload_data['phone_number'] = data['phone_number']
        batchload_data['fax'] = ''  # not provided in results but required for batch load file
        batchload_data['source'] = 'WEBVRTR'
        batchload_data['verified_data'] = batchload_file_date
        batchload_data['load_type'] = 'A'  # 'A' for 'Append'

        batchload_data.drop_duplicates(inplace=True)

        # save file to target directory
        batchload_filename = f'HSG_PHYS_WEBVRTR_PHONE_{batchload_file_date}.csv'
        batchload_save_path = f'{self._batch_load_save_dir}/{batchload_filename}'

        batchload_data.to_csv(batchload_save_path, index=False)
        LOGGER.info(f'Saved IT Batch Load file to: {batchload_save_path}')
        return batchload_data

    def _load_environment_variables(self):
        LOGGER.info('Loading environment variables for paths and connections')
        self._batch_load_save_dir = os.environ.get('BATCH_LOAD_SAVE_DIR')
        if self._database_path is None:
            self._database_path = os.environ.get('ARCHIVE_DB_PATH')
        if self.connection is None:
            self.connection = Connection(self._database_path)


def ingest_result_file(file_path):
    gen = VTPhysicianContactArchive()
    gen._load_environment_variables()

    # example:
    # file_dir = 'U:/Source Files/Data Analytics/Data-Science/Data/Vertical_Trail/Response/'
    # file_name = '2020-10-13_30000_VT_Sample_response_10_22_2020_10_39.csv'
    # file_path = file_dir + file_name

    gen.ingest_result_file(file_path=file_path)


def create_batchload_file_for_latest_results():
    gen = VTPhysicianContactArchive()
    gen._load_environment_variables()
    gen.create_batch_load_file(sample_id=gen.get_latest_results_sample_id())
