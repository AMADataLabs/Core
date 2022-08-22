package datalabs.etl.dag.state;

import java.lang.reflect.InvocationTargetException;
import java.util.Map;

import datalabs.parameter.Parameters;
import datalabs.etl.dag.state.Status;


public abstract class DagState {
    protected Parameters parameters = null;

    public DagState(Map<String, String> parameters, Class parameterClass)
            throws IllegalAccessException, InstantiationException, InvocationTargetException, NoSuchMethodException {
        this.parameters = Parameters.fromMap(parameters, parameterClass);
    }

    public abstract Status getDagStatus(String dag, String executionTime);

    public abstract Status getTaskStatus(String dag, String task, String executionTime);

    public abstract void setDagStatus(String dag, String executionTime, Status status);

    public abstract void setTaskStatus(String dag, String task, String executionTime, Status status);
}
