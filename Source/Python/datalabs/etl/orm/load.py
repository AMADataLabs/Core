"""OneView ETL ORM Loader"""
from   dataclasses import dataclass
import io
import logging
import math

import pandas
import sqlalchemy as sa

from   datalabs.access.orm import Database
from   datalabs.etl.orm.provider import get_provider
from   datalabs.parameter import add_schema
from   datalabs.plugin import import_plugin
from   datalabs.task import Task

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
    autoincrement: bool


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
    execution_time: str = None
    append: str = None
    delete: str = None
    ignore_columns: str = None
    soft_delete_column: str = None


class ORMLoaderTask(Task):
    PARAMETER_CLASS = ORMLoaderParameters

    COLUMN_TYPE_CONVERTERS = {
        'BOOLEAN': lambda x: x.map({'False': False, 'True': True}),
        'INTEGER': lambda x: x.astype(int, copy=False)
    }

    def run(self):
        LOGGER.debug('Input data: \n%s', self._data)
        model_classes = self._get_model_classes()
        data = [self._csv_to_dataframe(datum) for datum in self._data]

        with self._get_database() as database:
            for model_class, data in zip(model_classes, data):
                table_parameters = self._generate_table_parameters(database, model_class, data)

                self._update(database, table_parameters)

    def _get_database(self):
        return Database.from_parameters(self._parameters)

    def _get_model_classes(self):
        return [import_plugin(table) for table in self._parameters.model_classes.split(',')]

    @classmethod
    def _csv_to_dataframe(cls, data):
        dataframe = pandas.read_csv(io.BytesIO(data), dtype=object)

        return dataframe

    def _generate_table_parameters(self, database, model_class, data):
        schema = self._get_schema(model_class)
        table = model_class.__tablename__
        ignore_columns = self._get_ignore_columns()
        provider = self._get_provider()

        primary_key = provider.get_primary_key(database, schema, table)
        autoincrement = primary_key in ignore_columns
        columns = provider.get_database_columns(database, schema, table)
        hash_columns = self._get_hash_columns(columns, ignore_columns)

        if autoincrement:
            data[primary_key] = range(len(data))
        else:
            data[primary_key] = [str(key) for key in data[primary_key]]

        current_hashes = provider.get_current_row_hashes(database, schema, table, primary_key, hash_columns)
        incoming_hashes = provider.generate_row_hashes(data, primary_key, hash_columns)

        return TableParameters(data, model_class, primary_key, columns, current_hashes, incoming_hashes, autoincrement)

    @classmethod
    def _get_schema(cls, model_class):
        schema = None

        if hasattr(model_class, "__table_args__"):
            if hasattr(model_class.__table_args__, 'get'):
                schema = model_class.__table_args__.get('schema')
            else:
                for arg in model_class.__table_args__:
                    if hasattr(arg, 'get') and 'schema' in arg:
                        schema = arg.get('schema')

        return schema

    def _get_ignore_columns(self):
        ignore_columns = self._parameters.ignore_columns or ''
        ignore_columns = ignore_columns.split(',')

        return ignore_columns

    def _get_provider(self):
        try:
            provider = get_provider(self._parameters.database_backend)
        except ModuleNotFoundError as exception:
            dialect = self._parameters.database_backend.split('+')[0]
            raise ValueError(f"SQLAlchemy backend dialect '{dialect}' is not supported.") from exception

        return provider

    def _update(self, database, table_parameters):
        append = self._parameters.append
        delete = self._parameters.delete

        if append is None or append.upper() != 'TRUE' or (delete is not None and delete.upper() == 'TRUE'):
            self._delete_data(database, table_parameters)

        if delete is None or delete.upper() != 'TRUE' or (append is not None and append.upper() == 'TRUE'):
            self._update_data(database, table_parameters)

            self._add_data(database, table_parameters)

    @classmethod
    def _get_hash_columns(cls, columns, ignore_columns):
        hash_columns = columns

        for ignore_column in ignore_columns:
            if ignore_column in hash_columns:
                hash_columns.remove(ignore_column)

        return hash_columns

    def _delete_data(self, database, table_parameters):
        deleted_data = self._select_deleted_data(table_parameters)

        if self._parameters.soft_delete_column:
            self._soft_delete_data_from_table(database, table_parameters, deleted_data)
        else:
            self._delete_data_from_table(database, table_parameters, deleted_data)

        database.commit()  # pylint: disable=no-member

    @classmethod
    def _update_data(cls, database, table_parameters):
        updated_data = cls._select_updated_data(table_parameters)

        cls._update_data_in_table(database, table_parameters, updated_data)

        database.commit()  # pylint: disable=no-member

    @classmethod
    def _add_data(cls, database, table_parameters):
        added_data = cls._select_new_data(table_parameters)

        cls._add_data_to_table(database, table_parameters, added_data)

        database.commit()  # pylint: disable=no-member

    @classmethod
    def _select_deleted_data(cls, table_parameters):
        if table_parameters.autoincrement:
            deleted_data = table_parameters.current_hashes[
                ~table_parameters.current_hashes.md5.isin(table_parameters.incoming_hashes.md5)
            ].reset_index(drop=True)
        else:
            deleted_data = table_parameters.current_hashes[
                ~table_parameters.current_hashes[table_parameters.primary_key].isin(
                    table_parameters.data[table_parameters.primary_key]
                )
            ].reset_index(drop=True)
        LOGGER.debug('Deleted Data: %s', deleted_data)

        return deleted_data

    def _soft_delete_data_from_table(self, database, table_parameters, data):
        if not data.empty:
            deleted_models = self._get_deleted_models_from_table(database, table_parameters, data)
            count = 0

            for model in deleted_models:
                LOGGER.info('Soft deleting row: %s', getattr(model, table_parameters.primary_key))
                setattr(model, self._parameters.soft_delete_column, True)
                self._update_row_of_table(database, table_parameters, model)

                count += 1
                if count % 10000 == 0:
                    database.commit()  # pylint: disable=no-member

    @classmethod
    def _delete_data_from_table(cls, database, table_parameters, data):
        if not data.empty:
            deleted_models = cls._get_deleted_models_from_table(database, table_parameters, data)
            count = 0

            for model in deleted_models:
                LOGGER.info('Deleting row: %s', getattr(model, table_parameters.primary_key))
                database.delete(model)  # pylint: disable=no-member

                count += 1
                if count % 10000 == 0:
                    database.commit()  # pylint: disable=no-member

    @classmethod
    def _select_updated_data(cls, table_parameters):
        updated_data = pandas.DataFrame(columns=table_parameters.data.columns)

        if not table_parameters.autoincrement:
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
            count = 0

            for model in models:
                cls._update_row_of_table(database, table_parameters, model)

                count += 1
                if count % 10000 == 0:
                    database.commit()  # pylint: disable=no-member

    @classmethod
    def _select_new_data(cls, table_parameters):
        LOGGER.debug('DB data PK type: %s', table_parameters.current_hashes[table_parameters.primary_key].dtype)
        LOGGER.debug('Incoming data PK type: %s', table_parameters.data[table_parameters.primary_key].dtype)

        if table_parameters.autoincrement:
            selected_data = table_parameters.data[
                ~table_parameters.incoming_hashes.md5.isin(table_parameters.current_hashes.md5)
            ].reset_index(drop=True)
        else:
            selected_data = table_parameters.data[
                ~table_parameters.data[table_parameters.primary_key].isin(
                    table_parameters.current_hashes[table_parameters.primary_key]
                )
            ].reset_index(drop=True)
        LOGGER.debug('New Data: %s', selected_data)
        LOGGER.info('Incoming Data Size: %d', len(table_parameters.data))
        LOGGER.info('New Data Size: %d', len(selected_data))

        return selected_data

    @classmethod
    def _add_data_to_table(cls, database, table_parameters, data):
        if not data.empty:
            models = cls._create_models(table_parameters.model_class, data)
            count = 0

            for model in models:
                if table_parameters.autoincrement:
                    setattr(model, table_parameters.primary_key, None)

                database.add(model)  # pylint: disable=no-member

                count += 1
                if count % 10000 == 0:
                    database.commit()  # pylint: disable=no-member

    @classmethod
    def _create_models(cls, model_class, data):
        columns = cls._get_model_columns(model_class)

        cls._set_column_types(data, model_class, columns)

        for row in data.itertuples(index=False):
            yield cls._create_model(model_class, row, columns)

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
        columns = [column.key for column in mapper.attrs if hasattr(column, "columns")]

        return columns

    @classmethod
    def _create_model(cls, model_class, row, columns):
        parameters = {column: cls._replace_nan(getattr(row, column)) for column in columns if hasattr(row, column)}
        model = model_class(**parameters)

        return model

    @classmethod
    def _set_column_types(cls, data, model, columns):
        for column in columns:
            column_type = str(getattr(model, column).type)

            cls._set_column_type(data, column, column_type)

    @classmethod
    def _set_column_type(cls, data, column, column_type):
        if column_type in cls.COLUMN_TYPE_CONVERTERS:
            data[column] = cls.COLUMN_TYPE_CONVERTERS[column_type](data[column])

    @classmethod
    def _replace_nan(cls, value):
        replacement_value = value

        if isinstance(value, float) and math.isnan(value):
            replacement_value = None

        return replacement_value

class ORMPreLoaderTask(Task):
    def run(self):
        with self._get_database() as database:
            for model_class in self._get_model_classes():
                # pylint: disable=no-member
                database.delete(model_class)

            # pylint: disable=no-member
            database.commit()

    def _get_database(self):
        return Database.from_parameters(self._parameters)

    def _get_model_classes(self):
        return [import_plugin(table) for table in self._parameters['MODEL_CLASSES'].split(',')]


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class MaterializedViewRefresherParameters:
    database_host: str
    database_port: str
    database_name: str
    database_backend: str
    database_username: str
    database_password: str
    views: str
    execution_time: str = None


class MaterializedViewRefresherTask(Task):
    PARAMETER_CLASS = MaterializedViewRefresherParameters

    def run(self):
        with self._get_database() as database:
            views = []

            if self._parameters.views:
                views = [view.strip() for view in self._parameters.views.split(',')]

            for view in views:
                database.execute(f'REFRESH MATERIALIZED VIEW {view}')

            database.commit()  # pylint: disable=no-member

    def _get_database(self):
        return Database.from_parameters(self._parameters)


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class ReindexerParameters:
    database_host: str
    database_port: str
    database_name: str
    database_backend: str
    database_username: str
    database_password: str
    indexes: str = None
    tables: str = None
    execution_time: str = None


class ReindexerTask(Task):
    PARAMETER_CLASS = ReindexerParameters

    def run(self):
        with self._get_database() as database:
            indexes = []
            tables = []

            if self._parameters.indexes:
                indexes = [index.strip() for index in self._parameters.indexes.split(',')]

            if self._parameters.tables:
                tables = [index.strip() for index in self._parameters.tables.split(',')]

            for index in indexes:
                database.execute(f'REINDEX INDEX {index}')

            for table in tables:
                database.execute(f'REINDEX TABLE {table}')

            database.commit()  # pylint: disable=no-member

    def _get_database(self):
        return Database.from_parameters(self._parameters)
