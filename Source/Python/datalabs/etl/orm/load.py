"""OneView ETL ORM Loader"""
import hashlib
import io
import hashlib
import logging
import numpy
import pandas
import sqlalchemy as sa

from   datalabs.access.orm import Database
from   datalabs.task import DatabaseTaskMixin
from   datalabs.etl.load import LoaderTask
from   datalabs.plugin import import_plugin

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class ORMLoaderTask(LoaderTask, DatabaseTaskMixin):
    def __init__(self):
        super().__init__(parameters)
        self._data = None
        self._database = None
        self._table = None

    def _load(self):
        LOGGER.info(self._parameters)

        with self._get_database(Database, self._parameters) as database:
            for model_class, data, table in zip(self._get_model_classes(),
                                                self._get_dataframes(),
                                                self._parameters['TABLES']):
                self._data = data
                self._database = database
                self._table = table

                current_data = self._get_current_row_hashes()
                old_data, new_data, updated_data = self._compare_data(current_data)

                self._add_data(database, model_class, new_data)

            # pylint: disable=no-member
            database.commit()

    def _get_current_row_hashes(self):
        get_current_hash = "SELECT id, md5(f'{self._table}'::TEXT) FROM f'{self._table}'"
        hash_table = pandas.read_sql(get_current_hash, self._database)

        return hash_table

    def _compare_data(self, current_data):
        old_hashes = current_data.loc[current_data['md5'] in self._generate_row_hashes()]
        old_data = self._data.loc[self._data['id'] in old_hashes['id']]

        new_data = self._data.loc[self._data['id'] not in current_data['id']]

        updated_data = self._data.loc[self._data['id'] in current_data['id']]
        updated_data = updated_data.drop(updated_data['id'] in old_data['id'])

        return old_data, new_data, updated_data

    def _generate_row_hashes(self):
        columns = self._get_database_columns(self._database, self.table)
        csv_data = self._data[columns].to_csv(header=None, index=False).strip('\n').split('\n')
        row_strings = ["(" + i + ")" for i in csv_data]

        return [hashlib.md5(row_string.encode('utf-8')).hexdigest() for row_string in row_strings]

    @classmethod
    def _get_database_columns(cls, database, table):
        query = "SELECT * FROM information_schema.columns " \
                  f"WHERE table_schema = 'oneview' AND table_name = f'{table}';"
        old_data = pandas.read_sql(query, database)

        return old_data.columns

    @classmethod
    def _add_data(cls, database, model_class, data):
        models = [cls._create_model(model_class, row) for row in data.itertuples(index=False)]

        for model in models:
            # pylint: disable=no-member
            database.add(model)

    def _get_model_classes(self):
        return [import_plugin(table) for table in self._parameters['MODEL_CLASSES'].split(',')]

    def _get_dataframes(self):
        return [pandas.read_csv(io.BytesIO(data)) for data in self._parameters['data']]

    @classmethod
    def _create_model(cls, model_class, row):
        columns = cls._get_model_columns(model_class)
        parameters = {column: getattr(row, column) for column in columns if hasattr(row, column)}
        model = model_class(**parameters)

        return model

    @classmethod
    def _get_model_columns(cls, model_class):
        mapper = sa.inspect(model_class)
        columns = [column.key for column in mapper.attrs]

        return columns


class ORMPreLoaderTask(LoaderTask, DatabaseTaskMixin):
    def _load(self):
        with self._get_database(Database, self._parameters) as database:
            for model_class in self._get_model_classes():
                # pylint: disable=no-member
                database.delete(model_class)

            # pylint: disable=no-member
            database.commit()

    def _get_model_classes(self):
        return [import_plugin(table) for table in self._parameters['MODEL_CLASSES'].split(',')]
