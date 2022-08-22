""" SQLAlchemy Extractor """
from   datalabs.etl.sql.extract import SQLExtractorTask, SQLParametricExtractorTask, SQLParquetExtractorTask
from   datalabs.access.orm import Database

# pylint: disable=redefined-outer-name, protected-access
class SQLAlchemyConnectorMixin:
    def _connect(self):
        with self._get_database() as database:

            return database._connection.connection()

    def _get_database(self):
        return Database.from_parameters(
            dict(
                username=self._parameters.database_username,
                password=self._parameters.database_password,
                host=self._parameters.database_host,
                port=self._parameters.database_port,
                name=self._parameters.database_name,
                backend=self._parameters.driver
                )
        )

class JDBCExtractorTask(SQLAlchemyConnectorMixin, SQLExtractorTask):
    pass

class JDBCParametricExtractorTask(SQLAlchemyConnectorMixin, SQLParametricExtractorTask):
    pass

class JDBCParquetExtractorTask(SQLAlchemyConnectorMixin, SQLParquetExtractorTask):
    pass
