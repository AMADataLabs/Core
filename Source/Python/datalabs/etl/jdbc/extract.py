""" JDBC Extractor """
from   dataclasses import dataclass
import logging
from   pathlib import Path
import tempfile

import jaydebeapi
import pandas

from   datalabs.etl.extract import ExtractorTask
from   datalabs.parameter import add_schema

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


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
    database_port: str = None
    jar_path: str = None
    sql: str = None
    data: object = None
    execution_time: str = None
    chunk_size: str = None


class JDBCExtractorTask(ExtractorTask):
    PARAMETER_CLASS = JDBCExtractorParameters

    def _extract(self):
        connection = self._connect()

        return self._read_queries(connection)

    def _connect(self):
        url = f"jdbc:{self._parameters.driver_type}://{self._parameters.database_host}:" \
              f"{self._parameters.database_port}/{self._parameters.database_name}"
        print(url, self._parameters.jar_path.split(','), self._parameters.driver,
              [self._parameters.database_username, self._parameters.database_password])
        connection = jaydebeapi.connect(
            self._parameters.driver,
            url,
            [self._parameters.database_username, self._parameters.database_password],
            self._parameters.jar_path.split(',')
        )

        return connection

    def _read_queries(self, connection):
        queries = self._split_queries(self._parameters.sql)

        return [self._encode(self._read_query(query, connection)) for query in queries]

    @classmethod
    def _split_queries(cls, queries):
        queries_split = queries.split(';')
        queries_split.pop()

        return [q.strip() for q in queries_split]

    @classmethod
    def _encode(cls, data):
        return data.to_csv().encode('utf-8')

    def _read_query(self, query, connection):
        result = None

        if self._parameters.chunk_size is not None:
            result = self._read_chunked_query(query, connection)
        else:
            result = self._read_single_query(query, connection)

        return result

    def _read_chunked_query(self, query, connection):
        chunk_size = int(self._parameters.chunk_size)
        index = 0
        chunk = None
        results = None

        while chunk is None or len(chunk) > 0:
            resolved_query = query.format(index=index, count=chunk_size)

            LOGGER.info('Reading chunk at index %d...', index)
            chunk = self._read_single_query(resolved_query, connection)
            LOGGER.info('Read %d records.', len(chunk))
            LOGGER.info('Chunk memory usage:\n%s', chunk.memory_usage(deep=True))

            if len(chunk) > 0:
                if results is None:
                    results = chunk
                else:
                    results = pandas.concat([results, chunk], ignore_index=True)
                LOGGER.info('Concatenated chunks memory usage:\n%s', chunk.memory_usage(deep=True))
                index += chunk_size

        return results

    @classmethod
    def _read_single_query(cls, query, connection):
        return pandas.read_sql(query, connection)


class JDBCParquetExtractorTask(JDBCExtractorTask):
    PARAMETER_CLASS = JDBCExtractorParameters

    @classmethod
    def _encode(cls, data):
        return data

    def _read_chunked_query(self, query, connection):
        directory = tempfile.TemporaryDirectory()
        chunk_size = int(self._parameters.chunk_size)
        index = 0
        chunk = None

        while chunk is None or len(chunk) > 0:
            resolved_query = query.format(index=index, count=chunk_size)

            LOGGER.info('Reading chunk at index %d...', index)
            chunk = super()._read_single_query(resolved_query, connection)
            LOGGER.info('Read %d records.', len(chunk))

            if len(chunk) > 0:
                path = Path(directory.name, f'parquet_{index/chunk_size}')

                chunk.to_parquet(path)

                LOGGER.info('Wrote chunk to Parquet file %s', path)
                index += chunk_size

        return directory

    @classmethod
    def _read_single_query(cls, query, connection):
        directory = tempfile.TemporaryDirectory()
        results = pandas.read_sql(query, connection)
        path = Path(directory.name, 'parquet_0')

        results.to_parquet(path)

        return directory
