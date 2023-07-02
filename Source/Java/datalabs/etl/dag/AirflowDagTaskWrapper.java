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


public class AirflowDagTaskWrapper extends DagTaskWrapper {
    /* A DAG task wrapper for Airflow runtime environments.
     *
     * The DAG parameters are taken from an "args" task wrapper parameter which comprises a space-separated string
     * representing the command-line arguments (the first being the executable name). For Airflow, the second
     * command-line argument should be of the form DAG___TASK__EXECUTION-TIME.
     *
     * DAG task parameters are the same as the base class:
     * any environment variables of the form DAG__TASK__PARAMETER.
     */
    static final Logger LOGGER = LoggerFactory.getLogger(DagTaskWrapper.class);
    protected String dag;
    protected String task;
    protected String executionTime;

    public AirflowDagTaskWrapper(Map<String, String> environment, Map<String, String> parameters) {
        this.environment = environment;
        this.parameters = parseCommandLineArguments(parameters.get("args"));
    }

    protected Map<String, String> parseCommandLineArguments(String args) {
        Map<String, String> parameters = null;

        try {
            String[] commandLineArguments = args.split(" ", 2);

            if (commandLineArguments.length != 2) {
                throw new IllegalArgumentException(
                    "Expecting two command-line arguments (<executable name>, <DAG run ID>)."
                );
            }
            String[] parameterValues = commandLineArguments[1].split("__", 3);

            parameters = new HashMap<String, String>() {{
                put("dag", parameterValues[0]);
                put("task", parameterValues[1]);
                put("execution_time", parameterValues[2]);
            }};
        } catch (Exception exception) {
            throw new IllegalArgumentException("Unable to parse command-line parameters.", exception);
        }

        return parameters;
    }
}
