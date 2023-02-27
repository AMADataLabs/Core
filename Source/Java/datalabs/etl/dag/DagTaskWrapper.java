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
    static final Logger LOGGER = LoggerFactory.getLogger(DagTaskWrapper.class);

    public DagTaskWrapper(Map<String, String> environment, Map<String, String> parameters) {
        super(environment, parameters);
    }

    @Override
    protected Map<String, String> getRuntimeParameters(Map<String, String> parameters) throws TaskException {
        HashMap<String, String> runtimeParameters = null;

        try {
            if (!parameters.containsKey("args")) {
                throw new IllegalArgumentException("Missing \"args\" runtime parameter.");
            }
            String[] commandLineArguments = parameters.get("args").split(" ", 2);

            if (commandLineArguments.length != 2) {
                throw new IllegalArgumentException(
                    "Expecting two command-line arguments (<executable name>, <DAG run ID>)."
                );
            }
            String[] runtimeParameterValues = commandLineArguments[1].split("__", 3);

            runtimeParameters = new HashMap<String, String>() {{
                put("dag", runtimeParameterValues[0]);
                put("task", runtimeParameterValues[1]);
                put("execution_time", runtimeParameterValues[2]);
            }};
        } catch (Exception exception) {
            throw new TaskException("Unable to get runtime parameters.", exception);
        }

        return runtimeParameters;
    }

    @Override
    protected Map<String, String> getTaskParameters() throws TaskException {
        Map<String, String> taskParameters = null;

        try {
            Map<String, String> defaultParameters = this.getDefaultParameters();
            Map<String, String> dagTaskParameters = this.getDagTaskParameters();
            taskParameters = this.mergeParameters(defaultParameters, dagTaskParameters);
            LOGGER.debug("Raw Task Parameters: " + dagTaskParameters);

            LOGGER.debug("Runtime parameters BEFORE task parameter overrides: " + this.runtimeParameters);
            taskParameters.forEach(
                (key, value) -> overrideParameter(this.runtimeParameters, key, value)
            );
            LOGGER.debug("Runtime parameters AFTER task parameter overrides: " + this.runtimeParameters);
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

    protected Map<String, String> getDefaultParameters() {
        Map<String, String> dagParameters = getDefaultParametersFromEnvironment(getDagId());
        String execution_time = getExecutionTime();

        dagParameters.put("EXECUTION_TIME", execution_time);
        dagParameters.put("CACHE_EXECUTION_TIME", execution_time);

        return dagParameters;
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
        return this.runtimeParameters.get("dag").toUpperCase();
    }

    protected String getTaskId() {
        return this.runtimeParameters.get("task").toUpperCase();
    }

    protected String getExecutionTime() {
        return this.runtimeParameters.get("execution_time").toUpperCase();
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
