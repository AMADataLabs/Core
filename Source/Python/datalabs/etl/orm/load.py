"""OneView ETL ORM Loader"""
from   dataclasses import dataclass

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


@dataclass
class TableParameters:
    data: str
    table: str
    model_class: str
    primary_key: str
    columns: list
    current_hashes: pandas.DataFrame
    incoming_hashes: pandas.DataFrame


class ORMLoaderTask(LoaderTask, DatabaseTaskMixin):
    def _load(self):
        LOGGER.info(self._parameters)

        with self._get_database(Database, self._parameters) as database:
            for model_class, data, table in zip(self._get_model_classes(),
                                                self._get_dataframes(),
                                                self._parameters['TABLES']):

                table_parameters = self._generate_table_parameters(model_class, data, table, database)
                self._update(database, table_parameters)

            # pylint: disable=no-member
            database.commit()

    def _generate_table_parameters(self, model_class, data, table, database):
        primary_key = self._get_primary_key(database, table)
        columns = self._get_database_columns(database, table)

        current_hashes = self._get_current_row_hashes(database, table, primary_key)
        incoming_hashes = self._generate_row_hashes(columns, data, primary_key)

        return TableParameters(data, table, model_class, primary_key, columns, current_hashes, incoming_hashes)

    def _update(self, database, table_parameters):
        self._add_data(database, table_parameters)
        self._delete_data(database, table_parameters)
        self._update_data(database, table_parameters)

    @classmethod
    def _get_primary_key(cls, database, table):
        query = "SELECT a.attname, format_type(a.atttypid, a.atttypmod) AS data_type FROM pg_index i " \
                "JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey) " \
                f"WHERE  i.indrelid = f'{table}'::regclass AND i.indisprimary"

        primary_key_table = pandas.read_sql(query, database)

        return primary_key_table['attname'][0]

    @classmethod
    def _get_database_columns(cls, database, table):
        query = "SELECT * FROM information_schema.columns " \
                f"WHERE table_schema = 'oneview' AND table_name = f'{table}';"
        old_data = pandas.read_sql(query, database)

        return old_data.columns

    @classmethod
    def _get_current_row_hashes(cls, database, table, primary_key):
        get_current_hash = f"SELECT f'{primary_key}', md5(f'{table}'::TEXT) FROM f'{table}'"

        return pandas.read_sql(get_current_hash, database)

    @classmethod
    def _generate_row_hashes(cls, columns, data, primary_key):
        csv_data = data[columns].to_csv(header=None, index=False).strip('\n').split('\n')
        row_strings = ["(" + i + ")" for i in csv_data]

        hashes = [hashlib.md5(row_string.encode('utf-8')).hexdigest() for row_string in row_strings]
        primary_keys = data[primary_key].tolist()

        return pandas.DataFrame({primary_key: primary_keys, 'md5': hashes})

    @classmethod
    def _add_data(cls, database, table_parameters):
        added_data = cls._select_new_data(table_parameters)

        cls._add_data_to_table(table_parameters, added_data, database)

    @classmethod
    def _select_new_data(cls, table_parameters):
        return table_parameters.data[
            ~table_parameters.data[table_parameters.primary_key].isin(
                table_parameters.current_hashes[table_parameters.primary_key]
            )
        ].reset_index(drop=True)

    @classmethod
    def _add_data_to_table(cls, table_parameters, data, database):
        models = [cls._create_model(table_parameters.model_class, row) for row in data.itertuples(index=False)]

        for model in models:
            # pylint: disable=no-member
            database.add(model)

    @classmethod
    def _delete_data(cls, database, table_parameters):
        deleted_data = cls._select_deleted_data(table_parameters)

        cls._delete_data_from_table(table_parameters, deleted_data, database)

    @classmethod
    def _select_deleted_data(cls, table_parameters):
        return table_parameters.current_hashes[
            ~table_parameters.current_hashes[table_parameters.primary_key].isin(
                table_parameters.data[table_parameters.primary_key]
            )
        ].reset_index(drop=True)

    @classmethod
    def _delete_data_from_table(cls, table_parameters, data, database):
        deleted_primary_keys = data[table_parameters.primary_key].tolist()
        database_rows_query = f"SELECT * FROM {table_parameters.table} " \
                              f"WHERE {table_parameters.primary_key} IN {tuple(deleted_primary_keys)};"

        deleted_data = pandas.read_sql(database_rows_query, database)
        models = [cls._create_model(table_parameters.model_class, row) for row in deleted_data.itertuples(index=False)]

        for model in models:
            # pylint: disable=no-member
            database.delete(model)

    @classmethod
    def _update_data(cls, database, table_parameters):
        updated_data = cls._select_updated_data(table_parameters)

        cls._udpate_data_in_table(table_parameters, updated_data, database)

    @classmethod
    def _select_updated_data(cls, table_parameters):
        old_current_hashes = table_parameters.current_hashes[
            table_parameters.current_hashes[table_parameters.primary_key].isin(
                table_parameters.incoming_hashes[table_parameters.primary_key]
            )
        ]

        old_new_hashes = table_parameters.incoming_hashes[
            table_parameters.incoming_hashes[table_parameters.primary_key].isin(
                old_current_hashes[table_parameters.primary_key]
            )
        ]

        updated_hashes = old_new_hashes[~old_new_hashes['md5'].isin(old_current_hashes['md5'])]
        updated_data = table_parameters.data[
            table_parameters.data[table_parameters.primary_key].isin(
                updated_hashes[table_parameters.primary_key]
            )
        ]

        return updated_data.reset_index(drop=True)

    @classmethod
    def _update_data_in_table(cls, table_parameters, data, database):
        models = [cls._create_model(table_parameters.model_class, row) for row in data.itertuples(index=False)]

        for model in models:
            database.query().update(model)

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
