from datetime import datetime
from dateutil.relativedelta import relativedelta
import os
import pandas as pd
from sqlite3 import Connection

from datalabs.analysis.vertical_trail.physician_contact.column_definitions import *
import settings


class VTPhysicianContactArchive:
    def __init__(self, database_path=None):
        self.database_path = database_path
        self.connection = None
        if self.database_path is not None:
            self.connection = Connection(database_path)

        # column names of tables in database
        self.table_sample_columns = TABLE_SAMPLE_COLUMNS
        self.table_results_columns = TABLE_RESULTS_COLUMNS

        # column names of Excel files of samples sent to and results received from Vertical Trail
        self.file_sample_columns = FILE_SAMPLE_COLUMNS
        self.file_result_columns = FILE_RESULT_COLUMNS

        self.table_columns = {
            'vertical_trail_samples': self.table_sample_columns,
            'vertical_trail_results': self.table_results_columns
        }
        self.expected_file_columns = {
            'vertical_trail_samples': self.file_sample_columns,
            'vertical_trail_results': self.file_result_columns
        }

        self._batch_load_save_dir = None

    def _load_environment_variables(self):
        self._batch_load_save_dir = os.environ.get('BATCH_LOAD_SAVE_DIR')
        if self.database_path is None:
            self.database_path = os.environ.get('ARCHIVE_DB_PATH')
        if self.connection is None:
            self.connection = Connection(self.database_path)
