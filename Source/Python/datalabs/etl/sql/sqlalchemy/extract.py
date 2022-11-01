""" SQLAlchemy Extractor """
from   dataclasses import dataclass
import logging
import socket
from   urllib.parse import quote

from   datalabs.access.sqlalchemy import Database
from   datalabs.etl.sql.extract import SQLExtractorTask, SQLParametricExtractorTask, SQLParquetExtractorTask
from   datalabs.parameter import add_schema

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class SQLAlchemyExtractorParameters:
    backend: str
    database_host: str
    database_port: str
    database_username: str
    database_password: str
    sql: str
    execution_time: str = None
    chunk_size: str = None      # Number of records to fetch per chunk
    count: str = None           # Total number of records to fetch accross chunks
    start_index: str = '0'      # Starting record index
    max_parts: str = None       # Number of task copies working on this query
    part_index: str = None      # This task's index
    stream: str = None
    database_name: str = None
    database_parameters: str = None


# pylint: disable=redefined-outer-name, protected-access
class SQLAlchemyDatabaseMixin:
    PARAMETER_CLASS = SQLAlchemyExtractorParameters

    def _get_database(self):
        return Database(
            dict(
                USERNAME=self._parameters.database_username,
                PASSWORD=quote(self._parameters.database_password),
                HOST=self._parameters.database_host,
                PORT=self._parameters.database_port,
                NAME=self._parameters.database_name,
                BACKEND=self._parameters.backend
            )
        )

class SQLAlchemyExtractorTask(SQLAlchemyDatabaseMixin, SQLExtractorTask):
    pass

class SQLAlchemyParametricExtractorTask(SQLAlchemyDatabaseMixin, SQLParametricExtractorTask):
    pass

class SQLAlchemyParquetExtractorTask(SQLAlchemyDatabaseMixin, SQLParquetExtractorTask):
    pass
