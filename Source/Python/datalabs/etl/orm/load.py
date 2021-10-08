"""OneView ETL ORM Loader"""
import csv
from   dataclasses import dataclass
import io
import hashlib
import logging
import re

import pandas
import sqlalchemy as sa

from   datalabs.access.orm import Database
from   datalabs.etl.load import LoaderTask
from   datalabs.parameter import add_schema
from   datalabs.plugin import import_plugin

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=too-many-instance-attributes
@dataclass
class TableParameters:
    data: str
    model_class: str
    primary_key: str
    columns: list
    current_hashes: pandas.DataFrame
    incoming_hashes: pandas.DataFrame


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class ORMLoaderParameters:
    model_classes: str
    database_host: str
    database_port: str
    database_name: str
    database_backend: str
    database_username: str
    database_password: str
    data: object
    execution_time: str = None
    append: str = None


class ORMLoaderTask(LoaderTask):
    PARAMETER_CLASS = ORMLoaderParameters

    COLUMN_TYPES = {
        'BOOLEAN': bool,
        'INTEGER': int
    }

    def _load(self):
        LOGGER.info(self._parameters)
        model_classes = self._get_model_classes()
        data = [self._csv_to_dataframe(datum) for datum in self._parameters.data]

        with self._get_database() as database:
            for model_class, data in zip(model_classes, data):
                table_parameters = self._generate_table_parameters(database, model_class, data)

                self._update(database, table_parameters)

            # pylint: disable=no-member
            database.commit()

    def _get_database(self):
        return Database.from_parameters(
            dict(
                host=self._parameters.database_host,
                port=self._parameters.database_port,
                backend=self._parameters.database_backend,
                name=self._parameters.database_name,
                username=self._parameters.database_username,
                password=self._parameters.database_password
            )
        )

    def _get_model_classes(self):
        return [import_plugin(table) for table in self._parameters.model_classes.split(',')]

    @classmethod
    def _csv_to_dataframe(cls, data):
        dataframe = pandas.read_csv(io.BytesIO(data), dtype=object)

        dataframe.fillna('', inplace=True)

        return dataframe

    def _generate_table_parameters(self, database, model_class, data):
        schema = self._get_schema(model_class)
        table = model_class.__tablename__
        primary_key = self._get_primary_key(database, schema, table)
        columns = self._get_database_columns(database, schema, table)

        data[primary_key] = [str(key) for key in data[primary_key]]

        current_hashes = self._get_current_row_hashes(database, schema, table, primary_key)
        incoming_hashes = self._generate_row_hashes(columns, data, primary_key)

        return TableParameters(data, model_class, primary_key, columns, current_hashes, incoming_hashes)

    @classmethod
    def _get_schema(cls, model_class):
        if hasattr(model_class.__table_args__, 'get'):
            schema = model_class.__table_args__.get('schema')
        else:
            schema = model_class.__table_args__[1].get('schema')

        return schema

    def _update(self, database, table_parameters):
        self._add_data(database, table_parameters)

        self._update_data(database, table_parameters)

        if self._parameters.append is None or self._parameters.append.upper() != 'TRUE':
            self._delete_data(database, table_parameters)

    @classmethod
    def _get_primary_key(cls, database, schema, table):
        query = "SELECT a.attname, format_type(a.atttypid, a.atttypmod) AS data_type FROM pg_index i " \
                "JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey) " \
                f"WHERE  i.indrelid = '{schema}.{table}'::regclass AND i.indisprimary"

        primary_key_table = database.read(query)

        return primary_key_table['attname'][0]

    @classmethod
    def _get_database_columns(cls, database, schema, table):
        query = "SELECT * FROM information_schema.columns " \
                f"WHERE table_schema = '{schema}' AND table_name = '{table}';"
        column_data = database.read(query)

        columns = column_data.column_name.to_list()
        LOGGER.debug('Columns in table %s.%s: %s', schema, table, columns)

        return columns

    @classmethod
    def _get_current_row_hashes(cls, database, schema, table, primary_key):
        get_current_hash = f"SELECT {primary_key}, md5({table}::TEXT) FROM {schema}.{table}"

        current_hashes = database.read(get_current_hash).astype(str)
        LOGGER.debug('Current Row Hashes: %s', current_hashes)

        return current_hashes

    @classmethod
    def _generate_row_hashes(cls, columns, data, primary_key):
        csv_data = data[columns].to_csv(header=None, index=False, quoting=csv.QUOTE_ALL).strip('\n').split('\n')
        row_strings = ["(" + cls._remove_quotes(i) + ")" for i in csv_data]

        hashes = [hashlib.md5(row_string.encode('utf-8')).hexdigest() for row_string in row_strings]
        primary_keys = data[primary_key].tolist()

        incoming_hashes = pandas.DataFrame({primary_key: primary_keys, 'md5': hashes})
        LOGGER.debug('Incoming Row Hashes: %s', incoming_hashes)

        return incoming_hashes

    @classmethod
    def _add_data(cls, database, table_parameters):
        added_data = cls._select_new_data(table_parameters)

        cls._add_data_to_table(database, table_parameters, added_data)

    @classmethod
    def _update_data(cls, database, table_parameters):
        updated_data = cls._select_updated_data(table_parameters)

        cls._update_data_in_table(database, table_parameters, updated_data)

    @classmethod
    def _delete_data(cls, database, table_parameters):
        deleted_data = cls._select_deleted_data(table_parameters)

        cls._delete_data_from_table(database, table_parameters, deleted_data)

    @classmethod
    def _remove_quotes(cls, csv_string):
        # split at only unquoted commas
        columns = [term for term in re.split(r'("[^"]*,[^"]*"|[^,]*)', csv_string) if (term and term != ',')]

        return ','.join(cls._unquote_term(column) for column in columns)

    @classmethod
    def _select_new_data(cls, table_parameters):
        LOGGER.debug('DB data PK type: %s', table_parameters.current_hashes[table_parameters.primary_key].dtype)
        LOGGER.debug('Incoming data PK type: %s', table_parameters.data[table_parameters.primary_key].dtype)
        selected_data = table_parameters.data[
            ~table_parameters.data[table_parameters.primary_key].isin(
                table_parameters.current_hashes[table_parameters.primary_key]
            )
        ].reset_index(drop=True)
        LOGGER.debug('Selected Data: %s', selected_data)
        LOGGER.debug('Incoming Data Size: %d', len(table_parameters.data))
        LOGGER.debug('Selected Data Size: %d', len(selected_data))

        return selected_data

    @classmethod
    def _add_data_to_table(cls, database, table_parameters, data):
        if not data.empty:
            models = cls._create_models(table_parameters.model_class, data)

            for model in models:
                database.add(model)  # pylint: disable=no-member

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
        ].reset_index(drop=True)
        LOGGER.debug('Updated Data: %s', updated_data)

        return updated_data

    @classmethod
    def _update_data_in_table(cls, database, table_parameters, data):
        if not data.empty:
            models = cls._create_models(table_parameters.model_class, data)

            for model in models:
                cls._update_row_of_table(database, table_parameters, model)

    @classmethod
    def _select_deleted_data(cls, table_parameters):
        deleted_data = table_parameters.current_hashes[
            ~table_parameters.current_hashes[table_parameters.primary_key].isin(
                table_parameters.data[table_parameters.primary_key]
            )
        ].reset_index(drop=True)
        LOGGER.debug('Deleted Data: %s', deleted_data)

        return deleted_data

    @classmethod
    def _delete_data_from_table(cls, database, table_parameters, data):
        if not data.empty:
            deleted_models = cls._get_deleted_models_from_table(database, table_parameters, data)

            for model in deleted_models:
                database.delete(model)  # pylint: disable=no-member

    @classmethod
    def _unquote_term(cls, csv_column):
        quoted_csv_column = csv_column
        match = re.match(r'".*[, ].*"|""', csv_column)  # match quoted strings with spaces or commas

        if match is None:
            quoted_csv_column = f'{csv_column[1:-1]}'

        return quoted_csv_column

    @classmethod
    def _create_models(cls, model_class, data):
        columns = cls._get_model_columns(model_class)

        cls._set_column_types(data, model_class, columns)

        return [cls._create_model(model_class, row, columns) for row in data.itertuples(index=False)]

    @classmethod
    def _get_deleted_models_from_table(cls, database, table_parameters, data):
        primary_key = getattr(table_parameters.model_class, table_parameters.primary_key)
        deleted_keys = data[table_parameters.primary_key].tolist()

        return database.query(table_parameters.model_class).filter(primary_key.in_(tuple(deleted_keys))).all()

    @classmethod
    def _update_row_of_table(cls, database, table_parameters, model):
        columns = cls._get_model_columns(table_parameters.model_class)
        primary_key = getattr(model, table_parameters.primary_key)
        row = database.query(table_parameters.model_class).get(primary_key)
        for column in columns:
            setattr(row, column, getattr(model, column))

    @classmethod
    def _get_model_columns(cls, model_class):
        mapper = sa.inspect(model_class)
        columns = [column.key for column in mapper.attrs]

        return columns

    @classmethod
    def _create_model(cls, model_class, row, columns):
        parameters = {column: getattr(row, column) for column in columns if hasattr(row, column)}
        model = model_class(**parameters)

        return model

    @classmethod
    def _set_column_types(cls, data, model, columns):
        for column in columns:
            column_type = str(getattr(model, column).type)

            cls._set_column_type(data, column, column_type)

    @classmethod
    def _set_column_type(cls, data, column, column_type):
        if column_type in cls.COLUMN_TYPES:
            data[column] = data[column].astype(cls.COLUMN_TYPES[column_type], copy=False)


class ORMPreLoaderTask(LoaderTask):
    def _load(self):
        with self._get_database() as database:
            for model_class in self._get_model_classes():
                # pylint: disable=no-member
                database.delete(model_class)

            # pylint: disable=no-member
            database.commit()

    def _get_database(self):
        return Database.from_parameters(
            dict(
                host=self._parameters.database_host,
                port=self._parameters.database_port,
                backend=self._parameters.database_backend,
                name=self._parameters.database_name,
                username=self._parameters.database_username,
                password=self._parameters.database_password
            )
        )

    def _get_model_classes(self):
        return [import_plugin(table) for table in self._parameters['MODEL_CLASSES'].split(',')]
