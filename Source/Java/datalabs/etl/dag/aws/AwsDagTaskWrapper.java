package datalabs.etl.dag.aws;

import java.lang.reflect.InvocationTargetException;
import java.util.HashMap;
import java.util.Map;
import java.util.ArrayList;

import com.google.gson.Gson;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import datalabs.access.parameter.DynamoDbEnvironmentLoader;
import datalabs.etl.dag.DagTaskWrapper;
import datalabs.etl.dag.notify.sns.DagNotifier;
import datalabs.etl.dag.notify.sns.TaskNotifier;
import datalabs.etl.dag.state.DagState;
import datalabs.etl.dag.state.Status;
import datalabs.plugin.PluginImporter;
import datalabs.task.Task;
import datalabs.task.TaskException;


public class AwsDagTaskWrapper extends DagTaskWrapper {
    /* A DAG task wrapper for AWS runtime environments.
     *
     * The DAG and task parameters are retrieved from a DynamoDB table. To boostrap the retrieval of these parameters,
     * an environment variable named DYNAMODB_CONFIG_TABLE contains the name of the DynamoDB configuration table.
     *
     * A JSON string is expected to be passed to the task wrapper as the second command-line argument (the first being
     * the executable name). Once parsed, the resultant map comprises the DAG ID, task ID, and execution time
     * ("dag", "task", and "execution_time" items respectively).
     */
    static final Logger LOGGER = LoggerFactory.getLogger(AwsDagTaskWrapper.class);

    protected AwsDagTaskWrapper() { }

    public AwsDagTaskWrapper(Map<String, String> environment, Map<String, String> parameters) {
        this.environment = environment;
        this.parameters = parseCommandLineArguments(parameters.get("args"));

        if ("DAG".equals(this.parameters.get("type"))) {
            throw new UnsupportedOperationException("DAG processing is not supported in Java.");
        }

        LOGGER.info("DAG: " + this.parameters.get("dag"));
        LOGGER.info("Task: " + this.parameters.get("task"));
        LOGGER.info("Execution Time: " + this.parameters.get("execution_time"));

        if (this.environment.get("DYNAMODB_CONFIG_TABLE") == null) {
            throw new IllegalArgumentException("DYNAMODB_CONFIG_TABLE environment variable is not set.");
        }
    }

    protected void preRun() throws TaskException {
        try {
            setTaskStatus(Status.RUNNING);
        } catch (Exception exception) {
            throw new TaskException("Task finished, but unable to complete final DAG coordination.", exception);
        }
    }

    protected String handleSuccess() throws TaskException {
        super.handleSuccess();

        try {
            Map<String, String> pluginParameters = null;

            setTaskStatus(Status.FINISHED);

            notifyDagProcessor();
        } catch (Exception exception) {
            throw new TaskException("Task finished, but unable to complete final DAG coordination.", exception);
        }

        return "Success";
    }

    protected String handleException(Exception exception) {
        try {
            super.handleException(exception);

            Map<String, String> pluginParameters = null;

            setTaskStatus(Status.FAILED);

            notifyDagProcessor();
        } catch (Exception secondaryException) {
            LOGGER.error("An exception occurred while handling an exception from a task.", secondaryException);
        }

        return "Failed: " + exception.getMessage();
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

            parameters = new Gson().fromJson(commandLineArguments[1], HashMap.class);
        } catch (Exception exception) {
            throw new IllegalArgumentException("Unable to parse command-line parameters.", exception);
        }

        return parameters;
    }

    protected Map<String, String> getDagParameters() {
        Map<String, String> dagParameters = getDagTaskParametersFromDynamoDb(getDagId(), "DAG");

        dagParameters.put("CACHE_EXECUTION_TIME", getExecutionTime());

        return dagParameters;
    }

    protected Map<String, String> getDagTaskParameters() {
        String dag = getDagId();
        String task = getTaskId();
        LOGGER.debug("Getting DAG Task Parameters for " + dag + "__" + task);
        Map<String, String> dagTaskParameters = getDagTaskParametersFromDynamoDb(dag, task);

        LOGGER.debug("DAG Task Parameters: " + dagTaskParameters);
        return dagTaskParameters;
    }

    void setTaskStatus(Status status)
            throws ClassNotFoundException, NoSuchMethodException, InstantiationException, IllegalAccessException,
                   InvocationTargetException {
        DagState state = getDagStatePlugin(this.taskParameters);

        state.setTaskStatus(getDagId(), getTaskId(), getExecutionTime(), status);
    }

    void notifyTaskProcessor(Task task) {
        String topic = this.taskParameters.get("TASK_TOPIC_ARN");
        TaskNotifier notifier = new TaskNotifier(topic);

        notifier.notify(this.getDagId(), this.getTaskId(), this.getExecutionTime());
    }

    void notifyDagProcessor() {
        String topic = this.taskParameters.get("DAG_TOPIC_ARN");
        DagNotifier notifier = new DagNotifier(topic);

        notifier.notify(this.getDagId(), this.getExecutionTime());
    }

    protected Map<String, String> getDagTaskParametersFromDynamoDb(String dag, String task) {
        String[] dagIdParts = dag.split(":");
        String dagName = dagIdParts[0];
        HashMap<String, String> parameters = new HashMap<String, String>();

        DynamoDbEnvironmentLoader loader = new DynamoDbEnvironmentLoader(
            this.environment.get("DYNAMODB_CONFIG_TABLE"),
            dagName,
            task
        );

        return loader.load(parameters);
    }

    static DagState getDagStatePlugin(Map<String, String> taskParameters)
        throws ClassNotFoundException,
               NoSuchMethodException,
               InstantiationException,
               IllegalAccessException,
               InvocationTargetException
    {
        Class stateClass = null;
        Map<String, String> stateParameters = null;

        if (taskParameters.containsKey("DAG_STATE")) {
            stateParameters = new Gson().fromJson(taskParameters.get("DAG_STATE"), HashMap.class);
            stateClass = PluginImporter.importPlugin(stateParameters.get("CLASS"));
        } else {
            throw new IllegalArgumentException("Missing value for DAG parameter 'DAG_STATE_CLASS'");
        }

        return (DagState) stateClass.getConstructor(new Class[] {Map.class}).newInstance(stateParameters);
    }
}
