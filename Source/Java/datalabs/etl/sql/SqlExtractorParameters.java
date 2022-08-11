package datalabs.etl.sql;

import java.lang.reflect.InvocationTargetException;
import java.util.Map;

import datalabs.parameter.Parameters;
import datalabs.parameter.Optional;


public class SqlExtractorParameters extends Parameters {
    public String driver;
    public String driverType;
    public String databaseHost;
    public String databasePort;
    public String databaseUsername;
    public String databasePassword;
    public String sql;
    public Map<String, String> unknowns;

    @Optional
    public String execution_time;
    @Optional
    public String database_name;
    @Optional
    public String database_parameters;
    @Optional
    public String chunk_size;    // Number of records to fetch per chunk
    @Optional
    public String count;         // Total number of records to fetch accross chunks
    @Optional("0")
    public String start_index;   // Starting record index
    @Optional
    public String max_parts;     // Number of task copies working on this query
    @Optional
    public String part_index;    // This task's index
    @Optional
    public String stream;

    public SqlExtractorParameters(Map<String, String> parameters) throws IllegalAccessException, IllegalArgumentException, NoSuchFieldException {
        super(parameters);
    }
}
