""" JDBC Extractor """
from   dataclasses import dataclass

import jaydebeapi

from   datalabs.etl.sql.extract import SQLExtractorTask, SQLParametricExtractorTask, SQLParquetExtractorTask
from   datalabs.parameter import add_schema


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class JDBCExtractorParameters:
    driver: str
    driver_type: str
    database_host: str
    database_username: str
    database_password: str
    database_port: str
    jar_path: str
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



class JDBCConnectorMixin:
    PARAMETER_CLASS = JDBCExtractorParameters

    def _connect(self):
        url = f"jdbc:{self._parameters.driver_type}://{self._parameters.database_host}:" \
              f"{self._parameters.database_port}"

        if self._parameters.database_name is not None:
            url += f"/{self._parameters.database_name}"

        if self._parameters.database_parameters is not None:
            url += f";{self._parameters.database_parameters}"

        connection = jaydebeapi.connect(
            self._parameters.driver,
            url,
            [self._parameters.database_username, self._parameters.database_password],
            self._parameters.jar_path.split(',')
        )

        return connection

class JDBCExtractorTask(JDBCConnectorMixin, SQLExtractorTask):
    pass

class JDBCParametricExtractorTask(JDBCConnectorMixin, SQLParametricExtractorTask):
    pass

class JDBCParquetExtractorTask(JDBCConnectorMixin, SQLParquetExtractorTask):
    pass
