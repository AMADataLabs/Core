""" SQLAlchemy Extractor """
from   dataclasses import dataclass
from   urllib.parse import quote

import sqlalchemy
from   sqlalchemy.orm import sessionmaker

from   datalabs.access.orm import Database
from   datalabs.etl.sql.extract import SQLExtractorTask, SQLParametricExtractorTask, SQLParquetExtractorTask
from   datalabs.parameter import add_schema


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
    data: object = None
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
class SQLAlchemyConnectorMixin:
    PARAMETER_CLASS = SQLAlchemyExtractorParameters

    def _connect(self):
        database = self._get_database()
        engine = sqlalchemy.create_engine(database.url, echo=True)
        session = sessionmaker(bind=engine)()

        return session.connection().connection

    def _get_database(self):
        return Database.from_parameters(
            dict(
                username=self._database_username,
                password=quote(self._database_password),
                host=self._database_host,
                port=self._database_port,
                name=self._database_name,
                backend=self._parameters.backend
            )
        )

class SQLAlchemyExtractorTask(SQLAlchemyConnectorMixin, SQLExtractorTask):
    pass

class SQLAlchemyParametricExtractorTask(SQLAlchemyConnectorMixin, SQLParametricExtractorTask):
    pass

class SQLAlchemyParquetExtractorTask(SQLAlchemyConnectorMixin, SQLParquetExtractorTask):
    pass
