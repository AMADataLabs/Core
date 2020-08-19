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

    def get_vt_sample_data_past_n_months(self, n, as_of_date=datetime.now().date()):
        sql = """SELECT * FROM vertical_trail_samples"""
        data = pd.read_sql(sql=sql, con=self.connection)

        #data['survey_date'] = pd.to_datetime(data['survey_date'])
        #data['survey_date'] = data['survey_date'].apply(lambda x: x.date())

        data['month_diff'] = [relativedelta(as_of_date, sample_date) for sample_date in data['sample_date'].values]
        data['month_diff'] = data['month_diff'].apply(lambda x: x.months)

        data = data[data['month_diff'] <= int(n)]

        del data['month_diff']

        return data

    def _load_environment_variables(self):
        self._batch_load_save_dir = os.environ.get('BATCH_LOAD_SAVE_DIR')
        if self.database_path is None:
            self.database_path = os.environ.get('ARCHIVE_DB_PATH')
        if self.connection is None:
            self.connection = Connection(self.database_path)
