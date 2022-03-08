package datalabs.etl.dag.lambda;

import java.util.Map;

import datalabs.parameter.Parameters;


public class DagTaskWrapperParameters extends Parameters {
    public String dag;
    public String task;
    public String executionTime;
    public Map<String, String> unknowns;

    DagTaskWrapperParameters(Map<String, String> parameters) throws IllegalAccessException, IllegalArgumentException {
        super(parameters);
    }
}
