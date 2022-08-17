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
class SqlParametricExtractorTaskTests {
    protected static final Logger LOGGER = LoggerFactory.getLogger(SqlParametricExtractorTaskTests.class);

    static HashMap<String, String> SINGLE_QUERY_PARAMETER_MAP;
    static SqlExtractorParameters SINGLE_QUERY_PARAMETERS;
    static String SINGLE_QUERY_OUTPUT_CSV;
    static ResultSet SINGLE_QUERY_RESULTS;
    static HashMap<String, String> CHUNKED_QUERY_PARAMETER_MAP;
    static SqlExtractorParameters CHUNKED_QUERY_PARAMETERS;
    static String CHUNKED_QUERY_OUTPUT_CSV;
    static ResultSet CHUNKED_QUERY_RESULTS;
    static ResultSet EMPTY_RESULTS;
    static byte[] SQL_PARAMETERS_DATA;

    @Mock
    Connection connection;
    @Mock
    Statement statement;


    @BeforeEach
    void beforeEach() {
        SqlParametricExtractorTaskTests.SINGLE_QUERY_PARAMETER_MAP = new HashMap<String, String>() {{
            put("DRIVER_TYPE", "derby:memory");
            put("DATABASE_HOST", "");
            put("DATABASE_PORT", "");
            put("DATABASE_USERNAME", "AliBaba");
            put("DATABASE_PASSWORD", "OpenSesame");
            put("DATABASE_NAME", "pootitang");
            put("DATABASE_PARAMETERS", "create=true");
            put("SQL", "SELECT * FROM ping;SELECT * FROM pong;SELECT * FROM billabong;");
            put("MAX_PARTS", "5");
            put("PART_INDEX", "2");
        }};

        try {
            SqlParametricExtractorTaskTests.SINGLE_QUERY_PARAMETERS = new SqlExtractorParameters(
                SqlParametricExtractorTaskTests.SINGLE_QUERY_PARAMETER_MAP
            );
        } catch (Exception exception) {
            exception.printStackTrace();
        }


        SqlParametricExtractorTaskTests.CHUNKED_QUERY_PARAMETER_MAP = new HashMap<String, String>() {{
            put("DRIVER_TYPE", "derby:memory");
            put("DATABASE_HOST", "");
            put("DATABASE_PORT", "");
            put("DATABASE_USERNAME", "AliBaba");
            put("DATABASE_PASSWORD", "OpenSesame");
            put("DATABASE_NAME", "pootitang");
            put("DATABASE_PARAMETERS", "create=true");
            put("SQL", "SELECT * FROM ping LIMIT {index}, {count};SELECT * FROM pong LIMIT {index}, {count}");
            put("CHUNK_SIZE", "69");
            put("COUNT", "138");
            put("START_INDEX", "0");
            put("MAX_PARTS", "5");
            put("PART_INDEX", "3");
        }};

        try {
            SqlParametricExtractorTaskTests.CHUNKED_QUERY_PARAMETERS = new SqlExtractorParameters(
                SqlParametricExtractorTaskTests.CHUNKED_QUERY_PARAMETER_MAP
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

        SqlParametricExtractorTaskTests.SINGLE_QUERY_OUTPUT_CSV =
            "\"0001\",\"Johny Doe\"\n" +
            "\"0002\",\"Bob Smith\"\n" +
            "\"0003\",\"Alice Doe\"\n";

        SqlParametricExtractorTaskTests.CHUNKED_QUERY_OUTPUT_CSV =
            "\"AAAA\",\"Bill Bixby\"\n" +
            "\"BBBB\",\"Snoop Dogg\"\n" +
            "\"CCCC\",\"Fran Cella\"\n";

        SqlParametricExtractorTaskTests.SQL_PARAMETERS_DATA =
            ("\"year\",\"name\"\n" +
            "\"2022\",\"Jason Stathem\"\n" +
            "\"2012\",\"Jon Bon Jovi\"\n" +
            "\"2001\",\"Jennifer Aniston\"\n" +
            "\"1995\",\"Jimmy Falon\"\n" +
            "\"1988\",\"Joan Rivers\"\n").getBytes(StandardCharsets.UTF_8);


        try {
            SqlParametricExtractorTaskTests.SINGLE_QUERY_RESULTS = new Csv().read(
                new StringReader(SqlParametricExtractorTaskTests.SINGLE_QUERY_OUTPUT_CSV), new String[] {"id", "name"}
            );

            SqlParametricExtractorTaskTests.CHUNKED_QUERY_RESULTS = new Csv().read(
                new StringReader(SqlParametricExtractorTaskTests.CHUNKED_QUERY_OUTPUT_CSV), new String[] {"id", "name"}
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

        LOGGER.debug("Expected: |\"id\",\"name\"\n" + SqlParametricExtractorTaskTests.SINGLE_QUERY_OUTPUT_CSV + "|");
        LOGGER.debug("Actual: |" + outputCsv + "|");

        assertTrue(outputCsv.equals("\"id\",\"name\"\n" + SqlParametricExtractorTaskTests.SINGLE_QUERY_OUTPUT_CSV));
    }

    @Test
    public void readChunkedQueryReturnsCorrectData()  {
        setupChunkedQueryMockReturnValues();

        byte[] outputDatum = readChunkedQuery();

        assertNotNull(outputDatum);

        String outputCsv = new String(outputDatum, StandardCharsets.UTF_8);

        LOGGER.debug(
            "Expected: |\"id\",\"name\"\n" +
            SqlParametricExtractorTaskTests.SINGLE_QUERY_OUTPUT_CSV +
            SqlParametricExtractorTaskTests.CHUNKED_QUERY_OUTPUT_CSV +
            "|"
        );
        LOGGER.debug("Actual: |" + outputCsv + "|");

        assertTrue(outputCsv.equals(
            "\"id\",\"name\"\n" +
            SqlParametricExtractorTaskTests.SINGLE_QUERY_OUTPUT_CSV +
            SqlParametricExtractorTaskTests.CHUNKED_QUERY_OUTPUT_CSV
        ));
    }

    void setupSingleQueryMockReturnValues() {
        String resolvedQuery = "SELECT * FROM ping WHERE year='2001' AND name='Jennifer Aniston'";

        try {
            when(statement.executeQuery(resolvedQuery)).thenReturn(SqlParametricExtractorTaskTests.SINGLE_QUERY_RESULTS);
        } catch(java.sql.SQLException exception) {
            exception.printStackTrace();
        }
    }

    byte[] readSingleQuery() {
        byte[] outputDatum = null;

        try {
            SqlParametricExtractorTask task = new SqlParametricExtractorTask(
                SqlParametricExtractorTaskTests.SINGLE_QUERY_PARAMETER_MAP,
                new ArrayList<byte[]>() {{
                    add(SqlParametricExtractorTaskTests.SQL_PARAMETERS_DATA);
                }}
            );

            task.extractSqlParameters();

            outputDatum = task.readQuery(
                "SELECT * FROM ping WHERE year='{year}' AND name='{name}'",
                connection
            );
        } catch (Exception exception) {
            exception.printStackTrace();
            assertTrue(false);
        }

        return outputDatum;
    }

    void setupChunkedQueryMockReturnValues() {
        String resolvedBaseQuery = "SELECT * FROM ping WHERE year='1995' AND name='Jimmy Falon' LIMIT ";

        try {
            when(statement.executeQuery(resolvedBaseQuery + "0, 69")).thenReturn(SqlParametricExtractorTaskTests.SINGLE_QUERY_RESULTS);
            when(statement.executeQuery(resolvedBaseQuery + "69, 69")).thenReturn(SqlParametricExtractorTaskTests.CHUNKED_QUERY_RESULTS);
            when(statement.executeQuery(resolvedBaseQuery + "129, 69")).thenReturn(new EmptyResultSet());
        } catch(java.sql.SQLException exception) {
            exception.printStackTrace();
        }
    }

    byte[] readChunkedQuery() {
        byte[] outputDatum = null;

        try {
            SqlParametricExtractorTask task = new SqlParametricExtractorTask(
                SqlParametricExtractorTaskTests.CHUNKED_QUERY_PARAMETER_MAP,
                new ArrayList<byte[]>() {{
                    add(SqlParametricExtractorTaskTests.SQL_PARAMETERS_DATA);
                }}
            );

            task.extractSqlParameters();

            outputDatum = task.readQuery(
                "SELECT * FROM ping WHERE year='{year}' AND name='{name}' LIMIT {index}, {count}",
                connection
            );
        } catch (Exception exception) {
            exception.printStackTrace();
            assertTrue(false);
        }

        return outputDatum;
    }
}
