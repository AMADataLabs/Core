"""OneView ETL ORM Loader"""

import pandas

from   datalabs.access.orm import DatabaseTaskMixin
from   datalabs.etl.load import LoaderTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class OneViewORMLoader(LoaderTask, DatabaseTaskMixin):
    def __init__(self, parameters):
        super().__init__(parameters)

    def _load(self):
        with self._get_database(self._parameters.database) as database:
            self._connect = database.connect()  # pylint: disable=no-member
            for dataframe, table in zip(self._to_dataframe(), self._parameters.variables['TABLES'].split(',')):
                dataframe.to_sql(table, self._connect, if_exists='replace')

    def _to_dataframe(self):
        return [pandas.read_csv(data) for data in self._parameters.data]
