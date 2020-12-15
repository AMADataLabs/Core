""" JDBC Extractor """
import jaydebeapi
import pandas

from   datalabs.etl.extract import ExtractorTask


class JDBCExtractorTask(ExtractorTask):
    def _extract(self):
        connection = self._connect()

        return self._read_queries(connection)

    def _connect(self):
        url = f"jdbc:{self._parameters.variables['DRIVERTYPE']}://{self._parameters.database['host']}:" \
              f"{self._parameters.database['port']}/{self._parameters.database['name']}"

        connection = jaydebeapi.connect(
            self._parameters.variables['DRIVER'],
            url,
            [self._parameters.database['username'], self._parameters.database['password']],
            self._parameters.variables['JARPATH'].split(',')
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
