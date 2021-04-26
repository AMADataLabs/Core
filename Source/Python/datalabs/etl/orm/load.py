"""OneView ETL ORM Loader"""
import hashlib
import io
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
    def _load(self):
        LOGGER.info(self._parameters)

        with self._get_database(Database, self._parameters) as database:
            for model_class, data, table in zip(self._get_model_classes(),
                                                self._get_dataframes(),
                                                self._parameters['TABLES'].split(',')):

                current_data = self._get_current_data(database, model_class)
                data = self._generate_row_hashes(data)
                new_data = self._get_new_data(current_data, data)

                self._add_data(database, model_class, data)

            # pylint: disable=no-member
            database.commit()

    @classmethod
    def _add_data(cls, database, model_class, data):
        models = [cls._create_model(model_class, row) for row in data.itertuples(index=False)]

        for model in models:
            # pylint: disable=no-member
            database.add(model)

    def _get_current_data(self, database, model_class):
        get_current_hash = "SELECT pk, md5(mytable::TEXT) FROM mytable"

        return get_current_hash

    @classmethod
    def _generate_row_hashes(cls, dataframe):
        data = dataframe.to_csv(header=None, index=False).strip('\n').split('\n')
        hash_values = [hashlib.md5(row_string.encode('utf-8')).hexdigest() for row_string in data]
        dataframe['hash'] = hash_values

        return dataframe

    def _get_new_data(self, old_data, new_data):
        for row in new_data:
            for code in new_data['hash']:
                if code in old_data['md5']:
                    new_data.drop(row)

        for row in old_data:
            for code in old_data['md5']:
                if code not in new_data['hash']:
                    old_data.drop(row)

        return new_data, old_data

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
