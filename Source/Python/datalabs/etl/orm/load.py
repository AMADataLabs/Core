"""OneView ETL ORM Loader"""
import io
import logging
import pandas
import sqlalchemy as sa

from   datalabs.access.orm import DatabaseTaskMixin
from   datalabs.etl.load import LoaderTask
from   datalabs.plugin import import_plugin

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class ORMLoaderTask(LoaderTask, DatabaseTaskMixin):
    def _load(self):
        tables = [import_plugin(table) for table in self._parameters.variables['MODELCLASSES'].split(',')]

        with self._get_database(self._parameters.database) as database:
            for dataframe, table, model_class in zip(self._get_dataframes(),
                                                     self._parameters.variables['TABLES'].split(','),
                                                     tables):
                models = [self._create_model(row, model_class) for row in dataframe.itertuples(index=False)]
                for model in models:
                    database.session.add(model)

                database.session.commit()

    def _get_dataframes(self):
        return [pandas.read_csv(io.StringIO(data)) for data in self._parameters.data]

    def _create_model(self, row, model_class):
        columns = self._get_model_columns(model_class)
        parameters = {column: getattr(row, column) for column in columns if hasattr(row, column)}
        model = model_class(**parameters)

        return model

    def _get_model_columns(self, model_class):
        mapper = sa.inspect(model_class)
        columns = [column.key for column in mapper.attrs]

        return columns
