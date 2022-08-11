package datalabs.etl.sql;

import java.lang.reflect.InvocationTargetException;
import java.util.Map;

import datalabs.parameter.Parameters;


public class SqlExtractorParameters extends Parameters {
    public String driver;
    public String driverType;
    public String databaseHost;
    public String databasePort;
    public String databaseUsername;
    public String databasePassword;
    public Map<String, String> unknowns;

    public SqlExtractorParameters(Map<String, String> parameters) throws IllegalAccessException, IllegalArgumentException, NoSuchFieldException {
        super(parameters);
    }
}
/*
class JDBCExtractorParameters:
    driver: str
    driver_type: str
    database_host: str
    database_username: str
    database_password: str
    database_port: str
    jar_path: str
    sql: str
    data: object = None
    execution_time: str = None
    chunk_size: str = None      # Number of records to fetch per chunk
    count: str = None           # Total number of records to fetch accross chunks
    start_index: str = '0'      # Starting record index
    max_parts: str = None       # Number of task copies working on this query
    part_index: str = None      # This task's index
    stream: str = None
    database_name: str = None
    database_parameters: str = None
*/
