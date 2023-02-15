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


class QueryResults {
    public QueryResults(int rows, byte[] data) {
        this.rows = rows;
        this.data = data;
    }

    public int rows;
    public byte[] data;
}

class QueryIndices {
    public int start;
    public int stop;

    public QueryIndices(int start, int stop) {
        this.start = start;
        this.stop = stop;
    }
}


public class SqlExtractorTask extends Task {
    static final Logger LOGGER = LoggerFactory.getLogger(SqlExtractorTask.class);

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

    public Connection connect() throws SQLException, ClassNotFoundException {
        SqlExtractorParameters parameters = (SqlExtractorParameters) this.parameters;
        Properties credentials = generateCredentialProperties(parameters);
        String connectionString = generateConnectionString(parameters);

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
            if (query.toUpperCase().contains("INTO TEMP")) {
                LOGGER.debug("Temp table query: " + query);
                connection.createStatement().execute(query);
            } else {
                data.add(readQuery(query, connection));
            }
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
        SqlExtractorParameters parameters = (SqlExtractorParameters) this.parameters;
        QueryResults results = null;

        try (Statement statement = connection.createStatement()) {
            if (parameters.chunkSize.equals("")) {
                results = readSingleQuery(query, statement);
            } else {
                results = readChunkedQuery(query, statement, (SqlExtractorParameters) this.parameters);
            }
        }
        LOGGER.debug("Read " + results.rows + " rows (" + results.data.length + " bytes) from SQL query response.");

        return results.data;
    }

    static QueryResults readSingleQuery(String query, Statement statement, boolean includeHeaders)
            throws IOException, SQLException {
        return resultSetToQueryResults(statement.executeQuery(query), includeHeaders);
    }

    static QueryResults readSingleQuery(String query, Statement statement) throws IOException, SQLException {
        return readSingleQuery(query, statement, true);
    }

    static QueryResults readChunkedQuery(String query, Statement statement, SqlExtractorParameters parameters)
            throws IOException, SQLException {
        ArrayList<QueryResults> chunks = readChunks(query, statement, parameters);

        return concatenateQueryResults(chunks);
    }

    static QueryResults resultSetToQueryResults(ResultSet results, boolean includeHeaders) throws IOException, SQLException {
        ByteArrayOutputStream byteStream = new ByteArrayOutputStream();
        int rows = 0;
        byte[] csvBytes = new byte[0];

        try (byteStream; OutputStreamWriter streamWriter = new OutputStreamWriter(byteStream)) {
            CSVWriter writer = new CSVWriter(streamWriter);

            rows = writer.writeAll(results, includeHeaders);
            LOGGER.debug("Wrote " + rows + " rows to CSV bytes.");
        }

        if ((includeHeaders && rows > 1) || (!includeHeaders && rows > 0)) {
            csvBytes = byteStream.toByteArray();
        }

        return new QueryResults(includeHeaders?rows-1:rows, csvBytes);
    }

    static QueryResults resultSetToQueryResults(ResultSet results) throws IOException, SQLException {
        return resultSetToQueryResults(results, true);
    }

    static ArrayList<QueryResults> readChunks(String query, Statement statement, SqlExtractorParameters parameters)
            throws IOException, SQLException {
        ArrayList<QueryResults> chunks = new ArrayList<QueryResults>();
        int chunkSize = Integer.parseInt(parameters.chunkSize);
        QueryIndices queryIndices = SqlExtractorTask.calculateQueryIndices(parameters);
        int index = queryIndices.start;
        boolean iterating = true;
        boolean includeHeaders = true;

        while (iterating) {
            QueryResults chunk = null;

            if (queryIndices.stop >= 0 && (index + chunkSize) > queryIndices.stop) {
                chunkSize = queryIndices.stop - index;
            }

            LOGGER.debug("Stop Index: " + queryIndices.stop);
            LOGGER.debug("Index: " + index);
            LOGGER.debug("Chunk Size: " + chunkSize);

            if (chunkSize > 0) {
                String resolvedQuery = resolveChunkedQuery(query, index, chunkSize);
                LOGGER.debug("Unresolved Query: " + query);
                LOGGER.debug("Resolved Query: " + resolvedQuery);

                chunk = readSingleQuery(resolvedQuery, statement, includeHeaders);
            }

            if (queryIndices.stop >= 0 && index >= queryIndices.stop || chunkSize <= 0 || chunk.data.length == 0) {
                iterating = false;
            } else {
                chunks.add(chunk);

                index += chunk.rows;
            }

            includeHeaders = false;
        }

        return chunks;
    }

    static QueryResults concatenateQueryResults(ArrayList<QueryResults> chunks) {
        int totalResultsLength = 0;
        int totalRows = 0;
        int index = 0;
        byte[] data;

        for (QueryResults chunk : chunks) {
            totalResultsLength += chunk.data.length;
            totalRows += chunk.rows;
        }

        data = new byte[totalResultsLength];

        for (QueryResults chunk : chunks) {
            System.arraycopy(chunk.data, 0, data, index, chunk.data.length);

            index += chunk.data.length;
        }

        return new QueryResults(totalRows, data);
    }

    static QueryIndices calculateQueryIndices(SqlExtractorParameters parameters) {
        int count;
        QueryIndices queryIndices = new QueryIndices(0, -1);

        if (!parameters.count.equals("")) {
            count = Integer.parseInt(parameters.count);
            LOGGER.debug("COUNT: " + count);

            if (!parameters.startIndex.equals("")) {
                queryIndices.start = Integer.parseInt(parameters.startIndex) * count;
                LOGGER.debug("START_INDEX: " + queryIndices.start);
            }

            queryIndices.stop = queryIndices.start + count;
            LOGGER.debug("Stop Index: " + queryIndices.stop);
        }

        if (!parameters.maxParts.equals("") && !parameters.partIndex.equals("")) {
            int maxParts = Integer.parseInt(parameters.maxParts);
            int partIndex = Integer.parseInt(parameters.partIndex);

            if (partIndex >= (maxParts -1)) {
                queryIndices.stop = -1;
            }
        }

        return queryIndices;
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
