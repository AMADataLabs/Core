package datalabs.etl.dag.state.dynamodb;

import java.lang.reflect.InvocationTargetException;
import java.util.Map;

import datalabs.parameter.Parameters;


public class DagStateParameters extends Parameters {
    public String stateLockTable;
    public String dagStateTable;
    public Map<String, String> unknowns;

    public DagStateParameters(Map<String, String> parameters) throws IllegalAccessException, IllegalArgumentException {
        super(parameters);
    }
}
