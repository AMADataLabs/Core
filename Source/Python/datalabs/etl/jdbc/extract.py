"""JDBC Extractor"""
import os

import jaydebeapi
import pandas

from datalabs.etl.extract import ExtractorTask
from datalabs.etl.task import ETLException


class JDBCExtractor(ExtractorTask):
    def _extract(self):
        connection = self._connect()

        try:
            tables = self._read_queries_into_dataframe(connection)
        except Exception as exception:
            raise ETLException("Invalid SQL Statement") from exception

        return tables

    def _connect(self):
        url = f"jdbc:{self._parameters.variables['DRIVER_TYPE']}://{self._parameters.database['HOST']}:" \
              f"{self._parameters.database['PORT']}/{self._parameters.database['NAME']}"

        connection = jaydebeapi.connect(
            self._parameters.variables['DRIVER'],
            url,
            [self._parameters.database['username'], self._parameters.database['password']],
            self._parameters.variables['JAR_PATH']
        )

        return connection

    def _read_queries(self, connection):
        queries = self._split_queries(self._parameters.variables['SQL'])

        return [pandas.read_sql(query, connection) for query in queries]

    @classmethod
    def _split_queries(cls, queries):
        queries_split = queries.split(';')
        queries_split.pop()

        return [q.strip() for q in queries_split]
