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
    def _load(self):
        LOGGER.info(self._parameters)

        with self._get_database(Database, self._parameters) as database:
            for model_class, data in zip(self._get_model_classes(), self._get_dataframes()):

                self._add_data(database, model_class, data)

            # pylint: disable=no-member
            database.commit()

    @classmethod
    def _generate_row_hashes(cls, data, columns):
        csv_data = data[columns].to_csv(header=None, index=False).strip('\n').split('\n')
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

    @classmethod
    def _get_current_data(cls, database):
        get_current_hash = "SELECT pk, md5(f'{table}'::TEXT) FROM f'{table}'"
        hash_table = pandas.read_sql(get_current_hash, database)

        return hash_table

    @classmethod
    def _compare_data(cls, old_data, new_data):
        for generated_hash, db_hash in zip(cls._generate_row_hashes(), cls._get_current_data()['md5']):
            return db_hash

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
