package datalabs.etl.dag;

import java.util.HashMap;
import java.util.Map;
import java.util.ArrayList;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import datalabs.access.environment.VariableTree;
import datalabs.task.cache.TaskDataCache;
import datalabs.plugin.PluginImporter;
import datalabs.task.TaskException;
import datalabs.task.TaskWrapper;


public class DagTaskWrapper extends TaskWrapper {
    /* The base DAG task wrapper where the task parameters comprise DAG parameters
     * plus the DAG task parameters.
     *
     * The DAG parameters are just the task wrapper parameters, while the DAG task parameters are any
     * environment variables of the form DAG__TASK__PARAMETER.
     */
    static final Logger LOGGER = LoggerFactory.getLogger(DagTaskWrapper.class);

    protected DagTaskWrapper() { }

    public DagTaskWrapper(Map<String, String> environment, Map<String, String> parameters) {
        super(environment, parameters);
    }

    @Override
    protected Map<String, String> getTaskParameters() throws TaskException {
        Map<String, String> taskParameters = null;

        try {
            Map<String, String> dagParameters = this.getDagParameters();

            Map<String, String> dagTaskParameters = this.getDagTaskParameters();

            taskParameters = this.mergeParameters(dagParameters, dagTaskParameters);
        } catch (Exception exception) {
            throw new TaskException("Unable to get task parameters.", exception);
        }

        return taskParameters;
    }

    @Override
    protected String handleSuccess() throws TaskException {
        return null;
    }

    @Override
    protected String handleException(Exception exception) {
        LOGGER.error("Handling DAG task exception: " + exception.getMessage());
        exception.printStackTrace();

        return null;
    }

    @Override
    protected Class getTaskResolverClass() throws ClassNotFoundException {
        String taskResolverClassName = (String) this.environment.getOrDefault(
            "TASK_RESOLVER_CLASS",
            "datalabs.task.RuntimeTaskResolver"
        );

        return PluginImporter.importPlugin(taskResolverClassName);
    }

    protected Map<TaskDataCache.Direction, Map<String, String>> extractCacheParameters(Map<String, String> taskParameters) {
        Map<TaskDataCache.Direction, Map<String, String>> cacheParameters = super.extractCacheParameters(taskParameters);

        cacheParameters.get(TaskDataCache.Direction.INPUT).put("EXECUTION_TIME", getExecutionTime());

        cacheParameters.get(TaskDataCache.Direction.OUTPUT).put("EXECUTION_TIME", getExecutionTime());

        return cacheParameters;
    }

    protected Map<String, String> getDagParameters() {
        return this.parameters;
    }

    protected Map<String, String> getDagTaskParameters() {
        return getTaskParametersFromEnvironment(getDagId(), getTaskId());
    }

    Map<String, String> mergeParameters(Map<String, String> parameters, Map<String, String>  newParameters) {
        Map<String, String> mergedParameters = new HashMap<>(parameters);

        newParameters.forEach(
            (key, value) -> mergedParameters.merge(key, value, (oldValue, newValue) -> newValue)
        );

        return mergedParameters;
    }

    void overrideParameter(Map<String, String> parameters, String key, String value) {
        if (parameters.containsKey(key)) {
            parameters.put(key, value);
        }
    }

    protected String getDagId() {
        return this.parameters.get("dag").toUpperCase();
    }

    protected String getTaskId() {
        return this.parameters.get("task").toUpperCase();
    }

    protected String getExecutionTime() {
        return this.parameters.get("execution_time").toUpperCase();
    }

    static Map<String, String> getDefaultParametersFromEnvironment(String dagID) {
        Map<String, String> parameters;

        try {
            parameters = DagTaskWrapper.getParameters(new String[] {dagID.toUpperCase()});
        } catch (Exception exception) {  // FIXME: use a more specific exception
            parameters = new HashMap<String, String>();
        }

        return parameters;
    }

    static Map<String, String> getTaskParametersFromEnvironment(String dagID, String taskID) {
        Map<String, String> parameters;

        try {
            parameters = DagTaskWrapper.getParameters(new String[] {dagID.toUpperCase(), taskID.toUpperCase()});
        } catch (Exception exception) {  // FIXME: use a more specific exception
            parameters = new HashMap<String, String>();
        }

        return parameters;
    }

    static Map<String, String> getParameters(String[] branch) {
        VariableTree variableTree = VariableTree.fromEnvironment();

        Map<String, String> parameters = variableTree.getBranchValues(branch);
        LOGGER.debug("Branch Values: " + parameters);

        if (parameters == null) {
            parameters = new HashMap<String, String>();
        }
        LOGGER.debug("Environment Parameters: " + parameters);

        return parameters;
    }
}
