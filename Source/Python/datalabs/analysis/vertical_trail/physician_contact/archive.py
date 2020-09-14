from dataclasses import dataclass
from datetime import datetime
import os
from sqlite3 import Connection

from dateutil.relativedelta import relativedelta
import pandas as pd

from datalabs.analysis.vertical_trail.physician_contact.column_definitions import *
import settings

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
        return result

    def get_latest_results_sample_id(self):
        sql = "SELECT MAX(sample_id) FROM vertical_trail_results;"
        result = self.connection.execute(sql).fetchone()[0]
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
        data = pd.read_excel(file_path, dtype=str)
        self.ingest_sample_data(data)

    def ingest_sample_data(self, data: pd.DataFrame):
        data.fillna('', inplace=True)

        for i, r in data.iterrows():
            self.insert_row(table='vertical_trail_samples', vals=[v for v in r.values])
        self.connection.commit()

    def ingest_result_file(self, file_path: str):
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
        self.ingest_result_data(data=data)

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

        self.connection.execute(sql)

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
        self.connection.execute(sql)
        self.connection.commit()

    def _load_environment_variables(self):
        self._batch_load_save_dir = os.environ.get('BATCH_LOAD_SAVE_DIR')
        if self.database_path is None:
            self.database_path = os.environ.get('ARCHIVE_DB_PATH')
        if self.connection is None:
            self.connection = Connection(self.database_path)

