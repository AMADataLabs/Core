package datalabs.etl.dag.state;

import datalabs.parameter.Parameters;
import datalabs.etl.dag.state.Status;


public interface DagState {
    public Status getDagStatus(String dag, String executionTime);

    public Status getTaskStatus(String dag, String task, String executionTime);

    public void setDagStatus(String dag, String executionTime, Status status);

    public void setTaskStatus(String dag, String task, String executionTime, Status status);
}
