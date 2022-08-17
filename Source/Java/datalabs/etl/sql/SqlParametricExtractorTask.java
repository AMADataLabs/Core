package datalabs.etl.sql;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.lang.reflect.InvocationTargetException;
import java.sql.Connection;
import java.sql.SQLException;
import java.util.HashMap;
import java.util.Map;
import java.util.Vector;

import com.opencsv.CSVReader;
import com.opencsv.exceptions.CsvValidationException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import datalabs.string.PartialFormatter;
import datalabs.task.TaskException;


public class SqlParametricExtractorTask extends SqlExtractorTask {
    static final Logger LOGGER = LoggerFactory.getLogger(SqlParametricExtractorTask.class);

    Map<String, Object> sqlParameters = null;

    public SqlParametricExtractorTask(Map<String, String> parameters, Vector<byte[]> data)
            throws IllegalAccessException, InstantiationException, InvocationTargetException, NoSuchMethodException {
        super(parameters, data);
    }


    public Vector<byte[]> run() throws TaskException {
        try {
            int partIndex = Integer.parseInt(((SqlExtractorParameters) this.parameters).partIndex);

            sqlParameters = extractSqlParameters(this.inputData.get(0), partIndex);
        } catch (Exception exception) {
            throw new TaskException(exception);
        }

        return super.run();
    }


    Map<String, Object> extractSqlParameters(byte[] data, int partIndex) throws CsvValidationException, IOException {
        HashMap<String, Object> parameters = new HashMap<String, Object>();
        ByteArrayInputStream byteStream = new ByteArrayInputStream(data);
        String[] columns = null;
        String[] row = null;

        try (byteStream; InputStreamReader streamWriter = new InputStreamReader(byteStream)) {
            CSVReader reader = new CSVReader(streamWriter);

            columns = reader.readNext();

            reader.skip(partIndex);

            row = reader.readNext();
        }

        for (int index=0; index < columns.length; ++index) {
            parameters.put(columns[index], row[index]);
        }

        return parameters;
    }

    @Override
    byte[] readQuery(String query, Connection connection)
            throws IOException, SQLException {
        String resolvedQuery = resolveQuery(query, this.sqlParameters);

        return super.readQuery(resolvedQuery, connection);
    }

    String resolveQuery(String query, Map<String, Object> parameters) {
        PartialFormatter formatter = new PartialFormatter();

        return formatter.format(query, parameters);
    }
}
