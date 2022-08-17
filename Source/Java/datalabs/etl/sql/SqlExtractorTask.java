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
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;
import java.util.ArrayList;
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

    public SqlExtractorTask(Map<String, String> parameters, ArrayList<byte[]> data)
            throws IllegalAccessException, InstantiationException, InvocationTargetException, NoSuchMethodException {
        super(parameters, data, SqlExtractorParameters.class);
    }

    public ArrayList<byte[]> run() throws TaskException {
        ArrayList<byte[]> output;

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
            "jdbc:" + parameters.driverType;

        if (!parameters.databaseHost.equals("")) {
            connectionString += "://" + parameters.databaseHost + ":" + parameters.databasePort;

            if (!parameters.databaseName.equals("")) {
                connectionString += "/";
            }
        } else {
            if (!parameters.databaseName.equals("")) {
                connectionString += ":";
            }
        }

        if (!parameters.databaseName.equals("")) {
            connectionString += parameters.databaseName;
        }

        if (!parameters.databaseParameters.equals("")) {
            connectionString += ";" + parameters.databaseParameters;
        }

        return connectionString;
    }

    ArrayList<byte[]> readQueries(Connection connection) throws IOException, SQLException {
        String[] queries = splitQueries(((SqlExtractorParameters) this.parameters).sql);
        ArrayList<byte[]> data = new ArrayList<byte[]>();

        for (String query : queries) {
            data.add(readQuery(query, connection));
        }

        return data;
    }


    static String[] splitQueries(String queries) {
        String[] splitQueries = queries.split(";");

        for (int index=0; index < splitQueries.length; ++index) {
            splitQueries[index] = splitQueries[index].trim();
        }

        if (splitQueries[splitQueries.length-1].equals("")) {
            splitQueries = ArrayUtils.remove(splitQueries, splitQueries.length-1);
        }

        return splitQueries;
    }

    byte[] readQuery(String query, Connection connection) throws IOException, SQLException {
        byte[] results = null;

        try (Statement statement = connection.createStatement()) {
            if (((SqlExtractorParameters) this.parameters).chunkSize.equals("")) {
                results = readSingleQuery(query, statement);
            } else {
                results = readChunkedQuery(query, statement, (SqlExtractorParameters) this.parameters);
            }
        }

        return results;
    }

    static byte[] readSingleQuery(String query, Statement statement, boolean includeHeaders) throws IOException, SQLException {
        return resultSetToCsvBytes(statement.executeQuery(query), includeHeaders);
    }

    static byte[] readSingleQuery(String query, Statement statement) throws IOException, SQLException {
        return readSingleQuery(query, statement, true);
    }

    static byte[] readChunkedQuery(String query, Statement statement, SqlExtractorParameters parameters)
            throws IOException, SQLException {
        ArrayList<byte[]> csvChunks = readChunks(query, statement, parameters);

        return concatenateCsvChunks(csvChunks);
    }

    static byte[] resultSetToCsvBytes(ResultSet results, boolean includeHeaders) throws IOException, SQLException {
        ByteArrayOutputStream byteStream = new ByteArrayOutputStream();
        int rows = 0;
        byte[] csvBytes = new byte[0];

        try (byteStream; OutputStreamWriter streamWriter = new OutputStreamWriter(byteStream)) {
            CSVWriter writer = new CSVWriter(streamWriter);

            rows = writer.writeAll(results, includeHeaders);
        }

        if ((includeHeaders && rows > 1) || (!includeHeaders && rows > 0)) {
            csvBytes = byteStream.toByteArray();
        }

        return csvBytes;
    }

    static byte[] resultSetToCsvBytes(ResultSet results) throws IOException, SQLException {
        return resultSetToCsvBytes(results, true);
    }

    static ArrayList<byte[]> readChunks(String query, Statement statement, SqlExtractorParameters parameters)
            throws IOException, SQLException {
        ArrayList<byte[]> chunks = new ArrayList<byte[]>();
        int chunkSize = Integer.parseInt(parameters.chunkSize);
        int count;
        int index = 0;
        int stopIndex = -1;
        boolean iterating = true;
        boolean includeHeaders = true;

        if (parameters.count.equals("")) {
            count = Integer.parseInt(parameters.count);

            if (parameters.startIndex.equals("")) {
                index = Integer.parseInt(parameters.startIndex) * count;
                stopIndex = index + count;
            }
        }

        if (!parameters.maxParts.equals("") && !parameters.partIndex.equals("")) {
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
            LOGGER.debug("Unresolved Query: " + query);
            LOGGER.debug("Index: " + index);
            LOGGER.debug("Chunk Size: " + chunkSize);
            LOGGER.debug("Resolved Query: " + resolvedQuery);

            byte[] chunk = readSingleQuery(resolvedQuery, statement, includeHeaders);

            if (stopIndex >= 0 && index > stopIndex || chunk.length == 0) {
                iterating = false;
            } else {
                chunks.add(chunk);
            }

            includeHeaders = false;
            index += chunk.length;
        }

        return chunks;
    }

    static byte[] concatenateCsvChunks(ArrayList<byte[]> chunks) {
        int totalResultsLength = 0;
        int index = 0;
        byte[] results;

        for (byte[] chunk : chunks) {
            totalResultsLength += chunk.length;
        }

        results = new byte[totalResultsLength];

        for (byte[] chunk : chunks) {
            System.arraycopy(chunk, 0, results, index, chunk.length);

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
}
