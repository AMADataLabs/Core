package datalabs.etl.sql;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.lang.reflect.InvocationTargetException;
import java.sql.Connection;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.HashMap;
import java.util.Map;
import java.util.ArrayList;

import com.opencsv.CSVReader;
import com.opencsv.exceptions.CsvValidationException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import datalabs.string.PartialFormatter;
import datalabs.task.TaskException;


public class SqlParametricExtractorTask extends SqlExtractorTask {
    static final Logger LOGGER = LoggerFactory.getLogger(SqlParametricExtractorTask.class);

    HashMap<String, Object> sqlParameters = new HashMap<String, Object>();

    public SqlParametricExtractorTask(Map<String, String> parameters, ArrayList<byte[]> data)
            throws IllegalAccessException, InstantiationException, InvocationTargetException, NoSuchMethodException {
        super(parameters, data);
    }

    public ArrayList<byte[]> run() throws TaskException {
        try {
            extractSqlParameters();
        } catch (Exception exception) {
            throw new TaskException(exception);
        }

        return super.run();
    }

    void extractSqlParameters() throws CsvValidationException, IOException {
        int partIndex = Integer.parseInt(((SqlExtractorParameters) this.parameters).partIndex);
        ByteArrayInputStream byteStream = new ByteArrayInputStream(this.data.get(0));
        String[] columns = null;
        String[] row = null;

        try (byteStream; InputStreamReader streamWriter = new InputStreamReader(byteStream)) {
            CSVReader reader = new CSVReader(streamWriter);

            columns = reader.readNext();

            reader.skip(partIndex);

            row = reader.readNext();
        }

        for (int index=0; index < columns.length; ++index) {
            this.sqlParameters.put(columns[index], row[index]);
        }
    }

    @Override
    byte[] readQuery(String query, Connection connection) throws IOException, SQLException {
        String resolvedQuery = SqlParametricExtractorTask.resolveQuery(query, this.sqlParameters);

        return super.readQuery(resolvedQuery, connection);
    }

    static String resolveQuery(String query, Map<String, Object> parameters) {
        return PartialFormatter.format(query, parameters);
    }
}
