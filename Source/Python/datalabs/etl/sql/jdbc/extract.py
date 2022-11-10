""" JDBC Extractor """
from   dataclasses import dataclass

from   datalabs.access.jdbc import Database
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
    execution_time: str = None
    chunk_size: str = None      # Number of records to fetch per chunk
    count: str = None           # Total number of records to fetch accross chunks
    start_index: str = '0'      # Starting record index
    max_parts: str = None       # Number of task copies working on this query
    part_index: str = None      # This task's index
    stream: str = None
    database_name: str = None
    database_parameters: str = None



class JDBCDatabaseMixin:
    PARAMETER_CLASS = JDBCExtractorParameters

    def _get_database(self):
        parameters = dict(
                DRIVER=self._parameters.driver,
                DRIVER_TYPE=self._parameters.drivertype,
                HOST=self._parameters.database_host,
                USERNAME=self._parameters.database_username,
                PASSWORD=self._parameters.database_password,
                PORT=self._parameters.database_port,
                JAR_PATH=self._parameters.jar_path,
                NAME=self._parameters.database_name,
                PARAMETERS=self._parameters.parameters
        )

        if self._parameters.database_parameters:
            parameters["PARAMETERS"] = self._parameters.database_parameters

        return Database(parameters)

class JDBCExtractorTask(JDBCDatabaseMixin, SQLExtractorTask):
    pass

class JDBCParametricExtractorTask(JDBCDatabaseMixin, SQLParametricExtractorTask):
    pass

class JDBCParquetExtractorTask(JDBCDatabaseMixin, SQLParquetExtractorTask):
    pass
