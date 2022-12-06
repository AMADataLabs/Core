""" SQL Extractor """
from   dataclasses import dataclass
from   datetime import datetime
import logging
from   pathlib import Path
import string
import tempfile
from   abc import abstractmethod
import pandas

from   datalabs.access.database import Database
from   datalabs.etl.csv import CSVReaderMixin
from   datalabs.parameter import add_schema
from   datalabs.task import Task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class SQLExtractorParameters:
    sql: str
    execution_time: str = None
    chunk_size: str = None      # Number of records to fetch per chunk
    count: str = None           # Total number of records to fetch accross chunks
    start_index: str = '0'      # Starting record index
    max_parts: str = None       # Number of task copies working on this query
    part_index: str = None      # This task's index
    stream: str = None


class SQLExtractorTask(Task):
    PARAMETER_CLASS = SQLExtractorParameters

    def run(self):
        results = None

        with self._get_database() as database:
            results = self._read_queries(database.connection)

        return results

    @abstractmethod
    def _get_database(self) -> Database:
        pass

    def _read_queries(self, connection):
        queries = self._split_queries(self._parameters.sql)
        resolved_queries = self._resolve_time_format_codes(queries)

        if "INTO TEMP" in queries[0]:
            LOGGER.info("Executing temporary table query...")
            connection.cursor().execute(resolved_queries[0])

            resolved_queries.pop(0)

        return [self._encode(self._read_query(query, connection)) for query in resolved_queries]

    def _resolve_time_format_codes(self, queries):
        resolved_queries = queries

        if self._parameters.execution_time:
            execution_time = datetime.strptime(self._parameters.execution_time, "%Y-%m-%dT%H:%M:%S")

            resolved_queries = [execution_time.strftime(query) for query in queries]

        return resolved_queries

    @classmethod
    def _split_queries(cls, queries):
        queries_split = queries.split(';')

        if queries_split[-1].strip() == '':
            queries_split.pop()

        return [q.strip() for q in queries_split]

    @classmethod
    def _encode(cls, data):
        return data.to_csv(index=False).encode('utf-8')

    def _read_query(self, query, connection):
        result = None

        if self._parameters.chunk_size is None:
            result = self._read_single_query(query, connection)
        else:
            result = self._read_chunked_query(query, connection)

        return result

    def _read_chunked_query(self, query, connection):
        LOGGER.info('Sending chunked query: %s', query)
        chunks = self._iterate_over_chunks(query, connection)
        results = None

        if self._parameters.stream and self._parameters.stream.upper() == 'TRUE':
            results = chunks
        else:
            results = pandas.concat(list(chunks), ignore_index=True)
            LOGGER.info('Concatenated chunks memory usage:\n%s', results.memory_usage(deep=True))

        return results

    # pylint: disable=no-self-use
    def _read_single_query(self, query, connection):
        LOGGER.info('Sending query: %s', query)
        return pandas.read_sql(query, connection)

    def _iterate_over_chunks(self, query, connection):
        chunk_size = int(self._parameters.chunk_size)
        count = None
        index = 0
        stop_index = None
        iterating = True

        if self._parameters.count:
            count = int(self._parameters.count)
            index = 0

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

            resolved_query = self._resolve_chunked_query(query, index, chunk_size)

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
    def _resolve_chunked_query(self, query, index, count):
        formatter = PartialFormatter()

        if '{index}' not in query or '{count}' not in query:
            raise ValueError("Chunked query SQL does not contain '{index}' and '{count}' template variables.")

        return formatter.format(query, index=index, count=count)


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class SQLParametricExtractorParameters:
    driver: str
    driver_type: str
    database_host: str
    database_name: str
    database_username: str
    database_password: str
    database_port: str
    jar_path: str
    sql: str
    max_parts: str              # Number of task copies working on this query
    part_index: str             # This task's index
    execution_time: str = None
    chunk_size: str = None      # Number of records to fetch per chunk
    count: str = None           # Total number of records to fetch accross chunks
    start_index: str = '0'
    stream: str = None
    database_parameters: str = None


class SQLParametricExtractorTask(CSVReaderMixin, SQLExtractorTask):
    PARAMETER_CLASS = SQLParametricExtractorParameters

    def __init__(self, parameters: dict, data: "list<bytes>"):
        super().__init__(parameters, data)

        self._query_parameters = self._csv_to_dataframe(self._data[0])

    def _read_single_query(self, query, connection):
        resolved_query = self._resolve_query(query, 0, 0)

        return super()._read_single_query(resolved_query, connection)

    def _resolve_query(self, query, record_index, record_count):
        formatter = PartialFormatter()
        resolved_query = query

        if '{index}' in query and '{count}' in query:
            resolved_query = formatter.format(query, index=record_index, count=record_count)

        part_index = int(self._parameters.part_index)
        parameters = self._query_parameters.iloc[part_index].to_dict()

        return formatter.format(resolved_query, **parameters)


class SQLParquetExtractorTask(SQLExtractorTask):
    @classmethod
    def _encode(cls, data):
        return data

    def _read_chunked_query(self, query, connection):
        directory = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
        chunk_size = int(self._parameters.chunk_size)
        index = 0
        chunk = None

        while chunk is None or len(chunk) > 0:
            resolved_query = self._resolve_chunked_query(query, index, chunk_size)

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
        directory = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
        results = pandas.read_sql(query, connection)
        path = Path(directory.name, 'parquet_0')

        results.to_parquet(path)

        return directory

    @classmethod
    def _resolve_chunked_query(cls, query, index, count):
        if '{index}' not in query or '{count}' not in query:
            raise ValueError("Chunked query SQL does not contain '{index}' and '{count}' template variables.")

        return query.format(index=index, count=count)

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
