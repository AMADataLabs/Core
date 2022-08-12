package datalabs.etl.sql;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.lang.reflect.InvocationTargetException;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.Properties;
import java.sql.ResultSet;
import java.util.HashMap;
import java.util.Map;
import java.util.Vector;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerConfigurationException;
import javax.xml.transform.TransformerException;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamResult;

import com.opencsv.CSVWriter;
import org.apache.commons.lang3.ArrayUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.w3c.dom.Document;

import datalabs.string.PartialFormatter;
import datalabs.task.Task;
import datalabs.task.TaskException;


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

    public Vector<byte[]> run() throws TaskException {
        Vector<byte[]> output;

        try {
            Connection connection = connect();

            output = readQueries(connection);
        } catch (Exception exception) {
            throw new TaskException(exception);
        }

        return output;
    }

    public Connection connect() throws SQLException {
        Properties credentials = generateCredentialProperties((SqlExtractorParameters) this.parameters);
        String connectionString = generateConnectionString((SqlExtractorParameters) this.parameters);

        return DriverManager.getConnection(connectionString, credentials);
    }

    static Properties generateCredentialProperties(SqlExtractorParameters parameters) {
        Properties credentials = new Properties();

        credentials.put("user", parameters.databaseUsername);
        credentials.put("password", parameters.databasePassword);

        return credentials;
    }

    static String generateConnectionString(SqlExtractorParameters parameters) {
        String connectionString =
            "jdbc:" + parameters.driverType + "://" + parameters.databaseHost + ":" + parameters.databasePort;

        if (parameters.databaseName != "") {
            connectionString += "/" + parameters.databaseName;
        }

        if (parameters.databaseParameters != "") {
            connectionString += ";" + parameters.databaseParameters;
        }

        return connectionString;
    }

    Vector<byte[]> readQueries(Connection connection) throws IOException, SQLException {
        String[] queries = splitQueries(((SqlExtractorParameters) this.parameters).sql);
        Vector<byte[]> data = new Vector<byte[]>();

        for (String query : queries) {
            data.add(readQuery(query, connection, (SqlExtractorParameters) this.parameters));
        }

        return data;
    }


    static String[] splitQueries(String queries) {
        String[] splitQueries = queries.split(";");

        for (int index=0; index < splitQueries.length; ++index) {
            splitQueries[index] = splitQueries[index].trim();
        }

        if (splitQueries[splitQueries.length-1] == "") {
            splitQueries = ArrayUtils.remove(splitQueries, splitQueries.length-1);
        }

        return splitQueries;
    }

    byte[] readQuery(String query, Connection connection, SqlExtractorParameters parameters)
            throws IOException, SQLException {
        byte[] results = null;

        try (Statement statement = connection.createStatement()) {
            if (parameters.chunkSize == "") {
                results = readSingleQuery(query, statement);
            } else {
                results = readChunkedQuery(query, statement, parameters);
            }
        }

        return results;
    }

    static byte[] readSingleQuery(String query, Statement statement) throws IOException, SQLException {
        return resultSetToCsvBytes(statement.executeQuery(query));
    }

    byte[] readChunkedQuery(String query, Statement statement, SqlExtractorParameters parameters)
            throws IOException, SQLException {
        Vector<byte[]> csvChunks = readChunks(query, statement, parameters);

        return concatenateCsvChunks(csvChunks);
    }

    static byte[] resultSetToCsvBytes(ResultSet results, boolean includeHeaders) throws IOException, SQLException {
        ByteArrayOutputStream byteStream = new ByteArrayOutputStream();
        CSVWriter writer = new CSVWriter(new OutputStreamWriter(byteStream));

        writer.writeAll(results, includeHeaders);

        return byteStream.toByteArray();
    }

    static byte[] resultSetToCsvBytes(ResultSet results) throws IOException, SQLException {
        return resultSetToCsvBytes(results, true);
    }

    static Vector<byte[]> readChunks(String query, Statement statement, SqlExtractorParameters parameters)
            throws IOException, SQLException {
        Vector<byte[]> chunks = new Vector<byte[]>();
        int chunkSize = Integer.parseInt(parameters.chunkSize);
        int count;
        int index = 0;
        int stopIndex = -1;
        boolean iterating = true;

        if (parameters.count == "") {
            count = Integer.parseInt(parameters.count);

            if (parameters.startIndex == "") {
                index = Integer.parseInt(parameters.startIndex) * count;
                stopIndex = index + count;
            }
        }

        if (parameters.maxParts != "" && parameters.partIndex != "") {
            int maxParts = Integer.parseInt(parameters.maxParts);
            int partIndex = Integer.parseInt(parameters.partIndex);

            if (partIndex >= (maxParts -1)) {
                stopIndex = -1;
            }
        }

        while (iterating) {
            if (stopIndex >= 0 && (index + chunkSize) > stopIndex) {
                chunkSize = stopIndex - index;
            }

            String resolvedQuery = resolveChunkedQuery(query, index, chunkSize);

            byte[] chunk = readSingleQuery(resolvedQuery, statement);

            if (stopIndex >= 0 && (index > stopIndex || chunk.length == 0)) {
                iterating = false;
            } else {
                chunks.add(chunk);
            }

            index += chunk.length;
        }

        return chunks;
    }

    static Vector<byte[]> chunksToCsvBytes(Vector<ResultSet> resultSetChunks) throws IOException, SQLException {
        Vector<byte[]> csvChunks = new Vector<byte[]>();

        for (ResultSet chunk : resultSetChunks) {
            if (csvChunks.size() == 0) {
                csvChunks.add(resultSetToCsvBytes(chunk));
            } else {
                csvChunks.add(resultSetToCsvBytes(chunk, false));
            }
        }

        return csvChunks;
    }

    byte[] concatenateCsvChunks(Vector<byte[]> chunks) {
        int totalResultsLength = 0;
        int index = 0;
        byte[] results;

        for (byte[] chunk : chunks) {
            totalResultsLength += chunk.length;
        }

        results = new byte[totalResultsLength];

        for (byte[] chunk : chunks) {
            System.arraycopy(results, index, chunk, 0, index + chunk.length + 1);

            index += chunk.length;
        }

        return results;
    }

    static String resolveChunkedQuery(String query, int index, int count) {
        PartialFormatter formatter = new PartialFormatter();

        return formatter.format(
            query,
            new HashMap<String, Object>() {{
                put("index", index);
                put("count", count);
            }}
        );
    }
/*
    # pylint: disable=no-self-use
    def _resolve_chunked_query(self, query, index, count):
        formatter = PartialFormatter()

        if '{index}' not in query or '{count}' not in query:
            raise ValueError("Chunked query SQL does not contain '{index}' and '{count}' template variables.")

        return formatter.format(query, index=index, count=count)
*/
}
