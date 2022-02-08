package datalabs.etl.dag.state;

import java.lang.reflect.InvocationTargetException;
import java.util.Map;

import datalabs.parameter.ParameterizedClassMixin;
import datalabs.parameter.Parameters;
import datalabs.etl.dag.state.Status;


abstract public class DagState extends ParameterizedClassMixin {
    public DagState(Map<String, String> parameters)
            throws IllegalAccessException, InstantiationException, InvocationTargetException, NoSuchMethodException {
        super(parameters);
    }

    abstract public Status getDagStatus(String dag, String executionTime);

    abstract public Status getTaskStatus(String dag, String task, String executionTime);

    abstract public void setDagStatus(String dag, String executionTime, Status status);

    abstract public void setTaskStatus(String dag, String task, String executionTime, Status status);
}
