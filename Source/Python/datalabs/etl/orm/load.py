"""OneView ETL ORM Loader"""
import io
import hashlib
import logging
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
    def __init__(self, parameters):
        super().__init__(parameters)
        self._data = None
        self._database = None
        self._table = None
        self._model_class = None

    def _load(self):
        LOGGER.info(self._parameters)

        with self._get_database(Database, self._parameters) as database:
            for model_class, data, table in zip(self._get_model_classes(),
                                                self._get_dataframes(),
                                                self._parameters['TABLES']):
                self._data = data
                self._database = database
                self._table = table
                self._model_class = model_class

                self._update()

            # pylint: disable=no-member
            database.commit()

    def _update(self):
        primary_key = self._get_primary_key(self._database, self._table)
        columns = self._get_database_columns(self._database, self._table)

        current_hashes = self._get_current_row_hashes(self._database, self._table, primary_key)
        incoming_hashes = self._generate_row_hashes(columns, self._data, primary_key)

        new_data, updated_data, deleted_data = self._compare_data(self._data,
                                                                  current_hashes,
                                                                  incoming_hashes,
                                                                  primary_key)

        self._add_data(self._database, self._model_class, new_data)
        self._delete_data(self._database, self._model_class, deleted_data, primary_key, self._table)
        self._update_data(self._database, self._model_class, updated_data)

    @classmethod
    def _get_primary_key(cls, database, table):
        query = "SELECT a.attname, format_type(a.atttypid, a.atttypmod) AS data_type FROM pg_index i " \
                "JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey) " \
                f"WHERE  i.indrelid = f'{table}'::regclass AND i.indisprimary"

        primary_key_table = pandas.read_sql(query, database)

        return primary_key_table['attname'][0]

    @classmethod
    def _get_current_row_hashes(cls, database, table, primary_key):
        get_current_hash = f"SELECT f'{primary_key}', md5(f'{table}'::TEXT) FROM f'{table}'"

        return pandas.read_sql(get_current_hash, database)

    @classmethod
    def _compare_data(cls, data, current_hashes, incoming_hashes, primary_key):
        old_hashes = current_hashes[current_hashes[primary_key].isin(data[primary_key])]
        old_data = old_hashes[old_hashes['md5'].isin(incoming_hashes['md5'])]

        new_data = data[~data[primary_key].isin(current_hashes[primary_key])]

        updated_data = data[data[primary_key].isin(current_hashes[primary_key])]
        updated_data = updated_data[~updated_data[primary_key].isin(old_data[primary_key])]

        deleted_data = current_hashes[~current_hashes[primary_key].isin(data[primary_key])]

        return new_data.reset_index(drop=True), updated_data.reset_index(drop=True), deleted_data.reset_index(drop=True)

    @classmethod
    def _generate_row_hashes(cls, columns, data, primary_key):
        csv_data = data[columns].to_csv(header=None, index=False).strip('\n').split('\n')
        row_strings = ["(" + i + ")" for i in csv_data]

        hashes = [hashlib.md5(row_string.encode('utf-8')).hexdigest() for row_string in row_strings]
        primary_keys = data[primary_key].tolist()

        return pandas.DataFrame({primary_key: primary_keys, 'md5': hashes})

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

    @classmethod
    def _delete_data(cls, database, model_class, data, primary_key, table):
        deleted_primary_keys = data[primary_key].tolist()
        database_rows_query = f"SELECT * FROM {table} WHERE {primary_key} IN {tuple(deleted_primary_keys)};"

        data = pandas.read_sql(database_rows_query, database)
        models = [cls._create_model(model_class, row) for row in data.itertuples(index=False)]

        for model in models:
            # pylint: disable=no-member
            database.delete(model)

    @classmethod
    def _update_data(cls, database, model_class, data):
        models = [cls._create_model(model_class, row) for row in data.itertuples(index=False)]

        for model in models:
            database.query().update(model)


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
