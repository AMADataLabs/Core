package datalabs.etl.sql;

import java.io.InputStream;
import java.io.Reader;
import java.io.StringReader;
import java.nio.charset.StandardCharsets;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.Arrays;
import java.util.HashMap;
import java.util.ArrayList;

import org.h2.tools.Csv;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.when;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;


@ExtendWith(MockitoExtension.class)
class SqlExtractorTaskTests {
    protected static final Logger LOGGER = LoggerFactory.getLogger(SqlExtractorTaskTests.class);

    static HashMap<String, String> SINGLE_QUERY_PARAMETER_MAP;
    static SqlExtractorParameters SINGLE_QUERY_PARAMETERS;
    static String SINGLE_QUERY_OUTPUT_CSV;
    static ResultSet SINGLE_QUERY_RESULTS;
    static HashMap<String, String> CHUNKED_QUERY_PARAMETER_MAP;
    static SqlExtractorParameters CHUNKED_QUERY_PARAMETERS;
    static String CHUNKED_QUERY_OUTPUT_CSV;
    static ResultSet CHUNKED_QUERY_RESULTS;
    static ResultSet EMPTY_RESULTS;

    @Mock
    Connection connection;
    @Mock
    Statement statement;


    @BeforeEach
    void beforeEach() {
        SqlExtractorTaskTests.SINGLE_QUERY_PARAMETER_MAP = new HashMap<String, String>() {{
            put("DRIVER_TYPE", "derby:memory");
            put("DATABASE_HOST", "");
            put("DATABASE_PORT", "");
            put("DATABASE_USERNAME", "AliBaba");
            put("DATABASE_PASSWORD", "OpenSesame");
            put("DATABASE_NAME", "pootitang");
            put("DATABASE_PARAMETERS", "create=true");
            put("SQL", "SELECT * FROM ping;SELECT * FROM pong;SELECT * FROM billabong;");
        }};

        try {
            SqlExtractorTaskTests.SINGLE_QUERY_PARAMETERS = new SqlExtractorParameters(
                SqlExtractorTaskTests.SINGLE_QUERY_PARAMETER_MAP
            );
        } catch (Exception exception) {
            exception.printStackTrace();
        }


        SqlExtractorTaskTests.CHUNKED_QUERY_PARAMETER_MAP = new HashMap<String, String>() {{
            put("DRIVER_TYPE", "derby:memory");
            put("DATABASE_HOST", "");
            put("DATABASE_PORT", "");
            put("DATABASE_USERNAME", "AliBaba");
            put("DATABASE_PASSWORD", "OpenSesame");
            put("DATABASE_NAME", "pootitang");
            put("DATABASE_PARAMETERS", "create=true");
            put("SQL", "SELECT * FROM ping LIMIT {index}, {count};SELECT * FROM pong LIMIT {index}, {count}");
            put("CHUNK_SIZE", "3");
            put("COUNT", "6");
            put("START_INDEX", "2");
            // put("MAX_PARTS", "1");
            // put("PART_INDEX", "0");
        }};

        try {
            SqlExtractorTaskTests.CHUNKED_QUERY_PARAMETERS = new SqlExtractorParameters(
                SqlExtractorTaskTests.CHUNKED_QUERY_PARAMETER_MAP
            );
        } catch (Exception exception) {
            exception.printStackTrace();
        }

        try {
            Class.forName("org.apache.derby.jdbc.EmbeddedDriver").newInstance();
        } catch (
            java.lang.ClassNotFoundException | java.lang.InstantiationException |
            java.lang.IllegalAccessException exception
        ) {
            exception.printStackTrace();
        }

        SqlExtractorTaskTests.SINGLE_QUERY_OUTPUT_CSV =
            "\"0001\",\"Johny Doe\"\n" +
            "\"0002\",\"Bob Smith\"\n" +
            "\"0003\",\"Alice Doe\"\n";

        SqlExtractorTaskTests.CHUNKED_QUERY_OUTPUT_CSV =
            "\"AAAA\",\"Bill Bixby\"\n" +
            "\"BBBB\",\"Snoop Dogg\"\n" +
            "\"CCCC\",\"Fran Cella\"\n";


        try {
            SqlExtractorTaskTests.SINGLE_QUERY_RESULTS = new Csv().read(
                new StringReader(SqlExtractorTaskTests.SINGLE_QUERY_OUTPUT_CSV), new String[] {"id", "name"}
            );

            SqlExtractorTaskTests.CHUNKED_QUERY_RESULTS = new Csv().read(
                new StringReader(SqlExtractorTaskTests.CHUNKED_QUERY_OUTPUT_CSV), new String[] {"id", "name"}
            );
        } catch(java.io.IOException exception) {
            exception.printStackTrace();
        }

        try {
            when(connection.createStatement()).thenReturn(statement);
        } catch(java.sql.SQLException exception) {
            exception.printStackTrace();
        }
    }

    @Test
    public void readSingleQueryReturnsCorrectData()  {
        setupSingleQueryMockReturnValues();

        byte[] outputDatum = readSingleQuery();

        assertNotNull(outputDatum);

        String outputCsv = new String(outputDatum, StandardCharsets.UTF_8);

        LOGGER.debug("Expected: |\"id\",\"name\"\n" + SqlExtractorTaskTests.SINGLE_QUERY_OUTPUT_CSV + "|");
        LOGGER.debug("Actual: |" + outputCsv + "|");

        assertTrue(outputCsv.equals("\"id\",\"name\"\n" + SqlExtractorTaskTests.SINGLE_QUERY_OUTPUT_CSV));
    }

    @Test
    public void readChunkedQueryReturnsCorrectData()  {
        setupChunkedQueryMockReturnValues();

        byte[] outputDatum = readChunkedQuery();

        assertNotNull(outputDatum);

        String outputCsv = new String(outputDatum, StandardCharsets.UTF_8);

        LOGGER.debug(
            "Expected: |\"id\",\"name\"\n" +
            SqlExtractorTaskTests.SINGLE_QUERY_OUTPUT_CSV +
            SqlExtractorTaskTests.CHUNKED_QUERY_OUTPUT_CSV +
            "|"
        );
        LOGGER.debug("Actual: |" + outputCsv + "|");

        assertTrue(outputCsv.equals(
            "\"id\",\"name\"\n" +
            SqlExtractorTaskTests.SINGLE_QUERY_OUTPUT_CSV +
            SqlExtractorTaskTests.CHUNKED_QUERY_OUTPUT_CSV
        ));
    }

    void setupSingleQueryMockReturnValues() {
        try {
            when(statement.executeQuery("SELECT * FROM ping")).thenReturn(SqlExtractorTaskTests.SINGLE_QUERY_RESULTS);
        } catch(java.sql.SQLException exception) {
            exception.printStackTrace();
        }
    }

    byte[] readSingleQuery() {
        byte[] outputDatum = null;

        try {
            SqlExtractorTask task = new SqlExtractorTask(SqlExtractorTaskTests.SINGLE_QUERY_PARAMETER_MAP, null);

            outputDatum = task.readQuery("SELECT * FROM ping", connection);
        } catch (Exception exception) {
            exception.printStackTrace();
            assertTrue(false);
        }

        return outputDatum;
    }

    void setupChunkedQueryMockReturnValues() {
        try {
            when(statement.executeQuery("SELECT * FROM ping LIMIT 12, 3")).thenReturn(SqlExtractorTaskTests.SINGLE_QUERY_RESULTS);
            when(statement.executeQuery("SELECT * FROM ping LIMIT 15, 3")).thenReturn(SqlExtractorTaskTests.CHUNKED_QUERY_RESULTS);
        } catch(java.sql.SQLException exception) {
            exception.printStackTrace();
        }
    }

    byte[] readChunkedQuery() {
        byte[] outputDatum = null;

        try {
            SqlExtractorTask task = new SqlExtractorTask(SqlExtractorTaskTests.CHUNKED_QUERY_PARAMETER_MAP, null);

            outputDatum = task.readQuery("SELECT * FROM ping LIMIT {index}, {count}", connection);
        } catch (Exception exception) {
            exception.printStackTrace();
            assertTrue(false);
        }

        return outputDatum;
    }
}
