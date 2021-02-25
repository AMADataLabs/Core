""" JDBC Extractor """
from   dataclasses import dataclass

import jaydebeapi
import pandas

from   datalabs.etl.extract import ExtractorTask
from   datalabs.task import add_schema


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class JDBCExtractorParameters:
    driver: str
    driver_type: str
    database_host: str
    database_name: str = None
    database_username: str = None
    database_password: str = None
    jar_path: str = None
    sql: str = None
    data: object = None


class JDBCExtractorTask(ExtractorTask):
    PARAMETER_CLASS = JDBCExtractorParameters

    def _extract(self):
        connection = self._connect()

        return self._read_queries(connection)

    def _connect(self):
        url = f"jdbc:{self._parameters.driver_type}://{self._parameters.database_host}:" \
              f"{self._parameters.database_port}/{self._parameters.database_name}"

        connection = jaydebeapi.connect(
            self._parameters.driver,
            url,
            [self._parameters.database_username, self._parameters.database_password],
            self._parameters.jar_path.split(',')
        )

        return connection

    def _read_queries(self, connection):
        queries = self._split_queries(self._parameters.sql)

        return [pandas.read_sql(query, connection) for query in queries]

    @classmethod
    def _split_queries(cls, queries):
        queries_split = queries.split(';')
        queries_split.pop()

        return [q.strip() for q in queries_split]
