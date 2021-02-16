""" JDBC Extractor """
import jaydebeapi
import pandas

from   datalabs.etl.extract import ExtractorTask


class JDBCExtractorTask(ExtractorTask):
    def _extract(self):
        connection = self._connect()

        return self._read_queries(connection)

    def _connect(self):
        url = f"jdbc:{self._parameters.variables['DRIVER_TYPE']}://{self._parameters.variables['DATABASE_HOST']}:" \
              f"{self._parameters.variables['DATABASE_PORT']}/{self._parameters.variables['DATABASE_NAME']}"

        connection = jaydebeapi.connect(
            self._parameters.variables['DRIVER'],
            url,
            [self._parameters.variables['DATABASE_USERNAME'], self._parameters.variables['DATABASE_PASSWORD']],
            self._parameters.variables['JAR_PATH'].split(',')
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
