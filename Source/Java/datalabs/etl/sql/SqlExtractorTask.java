package datalabs.etl.sql;

import java.lang.reflect.InvocationTargetException;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.Properties;
import java.sql.BatchUpdateException;
import java.sql.DatabaseMetaData;
import java.sql.RowIdLifetime;
import java.sql.SQLWarning;
import java.util.Map;
import java.util.Vector;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerConfigurationException;
import javax.xml.transform.TransformerException;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamResult;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.w3c.dom.Document;

import datalabs.task.Task;


public class SqlExtractorTask extends Task {
    static final Logger LOGGER = LoggerFactory.getLogger(SqlExtractorTask.class);

    public SqlExtractorTask(Map<String, String> parameters)
            throws IllegalAccessException, InstantiationException, InvocationTargetException, NoSuchMethodException {
        super(parameters, SqlExtractorParameters.class);
    }

    public SqlExtractorTask(Map<String, String> parameters, Vector<byte[]> data)
            throws IllegalAccessException, InstantiationException, InvocationTargetException, NoSuchMethodException {
        super(parameters, data, SqlExtractorParameters.class);
    }

    public Vector<byte[]> run() {
        // Connection connection = this.connect();
        //
        // return this.read_queries(connection);
        return null;
    }
/*
    public Connection connect() throws SQLException {
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

    def _read_queries(self, connection):
        queries = self._split_queries(self._parameters.sql)

        return [self._encode(self._read_query(query, connection)) for query in queries]

    @classmethod
    def _split_queries(cls, queries):
        queries_split = queries.split(';')

        if queries_split[-1].strip() == '':
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
*/
}
