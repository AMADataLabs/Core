"""OneView ETL ORM Loader"""
import io
import logging
import pandas
import sqlalchemy as sa

from datalabs.access.orm import DatabaseTaskMixin
from datalabs.etl.load import LoaderTask
import datalabs.model.masterfile.oneview as dbmodel

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class ORMLoader(LoaderTask, DatabaseTaskMixin):
    def _load(self):
        with self._get_database(self._parameters.database) as database:
            self._connect = database.session

            for dataframe, table in zip(self._to_dataframe(), self._parameters.variables['TABLES'].split(',')):
                query = sa.insert(dbmodel.Physician)
                import pdb
                pdb.set_trace()
                self._connect.execute(query, dataframe)

                # dataframe.to_sql(table, self._connect, if_exists='replace')

    def _to_dataframe(self):
        return [pandas.read_csv(io.StringIO(data)) for data in self._parameters.data]
