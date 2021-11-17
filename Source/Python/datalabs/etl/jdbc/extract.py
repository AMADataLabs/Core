""" JDBC Extractor """
from   dataclasses import dataclass
import logging
from   pathlib import Path
import string
import tempfile

import jaydebeapi
import pandas

from   datalabs.etl.extract import ExtractorTask
from   datalabs.etl.csv import CSVReaderMixin
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
    database_name: str
    database_username: str
    database_password: str
    database_port: str
    jar_path: str
    sql: str
    data: object = None
    execution_time: str = None
    chunk_size: str = None
    count: str = None
    start_index: str = '0'
    max_parts: str = None
    part_index: str = None
    stream: str = None


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

        return [self._encode(self._read_query(query, connection)) for query in queries]

    @classmethod
    def _split_queries(cls, queries):
        queries_split = queries.split(';')

        if queries_split[-1] == '':
            queries_split.pop()

        return [q.strip() for q in queries_split]

    @classmethod
    def _encode(cls, data):
        return data.to_csv().encode('utf-8')

    def _read_query(self, query, connection):
        LOGGER.info('Sending query: %s', query)
        result = None

        if self._parameters.chunk_size is not None:
            result = self._read_chunked_query(query, connection)
        else:
            result = self._read_single_query(query, connection)

        return result

    def _read_chunked_query(self, query, connection):
        chunks = self._iterate_over_chunks(query, connection)
        results = None

        if self._parameters.stream and self._parameters.stream.upper() == 'TRUE':
            results = chunks
        else:
            results = pandas.concat(list(chunks), ignore_index=True)
            LOGGER.info('Concatenated chunks memory usage:\n%s', results.memory_usage(deep=True))

        return results

    @classmethod
    def _read_single_query(cls, query, connection):
        return pandas.read_sql(query, connection)

    def _iterate_over_chunks(self, query, connection):
        chunk_size = int(self._parameters.chunk_size)
        count = None
        index = 0
        stop_index = None
        iterating = True

        if self._parameters.count:
            count = int(self._parameters.count)

            if self._parameters.start_index:
                index = int(self._parameters.start_index) * count
                stop_index = index + count

        if self._parameters.max_parts is not None and self._parameters.part_index is not None:
            max_parts = int(self._parameters.max_parts)
            part_index = int(self._parameters.part_index)

            if part_index >= (max_parts - 1):
                stop_index = None

        while iterating:
            if stop_index and (index + chunk_size) > stop_index:
                chunk_size = stop_index - index

            resolved_query = self._resolve_query(query, index, chunk_size)

            LOGGER.info('Reading chunk of size %d at index %d...', chunk_size, index)
            chunk = self._read_single_query(resolved_query, connection)
            read_count = len(chunk)
            LOGGER.info('Read %d records.', read_count)
            LOGGER.info('Chunk memory usage:\n%s', chunk.memory_usage(deep=True))

            if stop_index and index > stop_index or read_count == 0:
                iterating = False
            else:
                yield chunk

            index += read_count

    # pylint: disable=no-self-use
    def _resolve_query(self, query, record_index, record_count):
        formatter = PartialFormatter()

        return formatter.format(query, index=record_index, count=record_count)


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class JDBCParametricExtractorParameters:
    driver: str
    driver_type: str
    database_host: str
    database_name: str
    database_username: str
    database_password: str
    database_port: str
    jar_path: str
    sql: str
    max_parts: str
    part_index: str
    data: object = None
    execution_time: str = None
    chunk_size: str = None
    count: str = None
    start_index: str = '0'
    stream: str = None


class JDBCParametricExtractorTask(CSVReaderMixin, JDBCExtractorTask):
    PARAMETER_CLASS = JDBCParametricExtractorParameters

    def __init__(self, parameters):
        super().__init__(parameters)

        self._query_parameters = self._csv_to_dataframe(self._parameters.data[0])

    def _resolve_query(self, query, record_index, record_count):
        formatter = PartialFormatter()
        resolved_query = super()._resolve_query(query, record_index, record_count)
        part_index = int(self._parameters.part_index)
        parameters = self._query_parameters.iloc[part_index].to_dict()

        return formatter.format(resolved_query, **parameters)


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

class PartialFormatter(string.Formatter):
    def __init__(self, default='{{{0}}}'):
        self.default=default

    def get_value(self, key, args, kwargs):
        formatted_value = None

        if isinstance(key, str):
            formatted_value = kwargs.get(key, self.default.format(key))
        else:
            formatted_value = super().get_value(key, args, kwargs)

        return formatted_value
