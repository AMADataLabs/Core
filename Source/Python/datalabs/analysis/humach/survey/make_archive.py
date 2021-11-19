""" SQLite Humach Database creation -- will be deleted """
# pylint: disable=no-name-in-module,import-error,wildcard-import,undefined-variable,protected-access,unused-import
import os
from sqlite3 import Connection
from datalabs.analysis.humach.survey.sql_statements import *

import settings


class ArchiveMaker:
    def __init__(self, database_path=None):
        self.database_path = database_path
        self.connection = None
        if self.database_path is not None:
            self.connection = Connection(self.database_path)

    def initialize_tables(self):
        self._load_environment_variables()
        self._drop_archive_tables()
        self._make_archive_tables()

    def _drop_archive_tables(self):
        self._drop_table_samples()
        self._drop_table_results()
        self._drop_table_validation_result()
        self._drop_table_reference()
        self.connection.commit()

    def _make_archive_tables(self):
        self._make_table_samples()
        self._make_table_results()
        self._make_table_validation_result()
        self._make_table_reference()
        self.connection.commit()

    def _make_table_samples(self):
        sql = MAKE_TABLE_SAMPLES
        self.connection.execute(sql)

    def _make_table_results(self):
        sql = MAKE_TABLE_RESULTS
        self.connection.execute(sql)

    def _make_table_reference(self):
        sql = MAKE_TABLE_REFERENCE
        self.connection.execute(sql)

    def _make_table_validation_result(self):
        self.connection.execute(MAKE_TABLE_VALIDATION_RESULT)

    def _drop_table_samples(self):
        sql = DROP_TABLE_SAMPLES
        self.connection.execute(sql)

    def _drop_table_results(self):
        sql = DROP_TABLE_RESULTS
        self.connection.execute(sql)

    def _drop_table_reference(self):
        sql = DROP_TABLE_REFERENCE
        self.connection.execute(sql)

    def _drop_table_validation_result(self):
        self.connection.execute(DROP_TABLE_VALIDATION_RESULT)

    def _load_environment_variables(self):
        if self.database_path is None:
            self.database_path = os.environ.get('ARCHIVE_DB_PATH')
        if self.connection is None:
            self.connection = Connection(self.database_path)


if __name__ == '__main__':
    archive = ArchiveMaker()
    #archive.initialize_tables()
    archive._load_environment_variables()
    archive._drop_table_results()
    archive._make_table_results()
    #archive._drop_table_reference()
    #archive._make_table_reference()

    archive.connection.commit()
