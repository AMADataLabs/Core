package datalabs.etl.dag.aws;

import java.lang.reflect.InvocationTargetException;
import java.util.HashMap;
import java.util.Map;
import java.util.ArrayList;

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


public class AwsDagTaskWrapper extends DagTaskWrapper {
    static final Logger LOGGER = LoggerFactory.getLogger(AwsDagTaskWrapper.class);
    Map<String, String> taskParameters;

    public AwsDagTaskWrapper(Map<String, String> environment, Map<String, String> parameters) {
        super(environment, parameters);

        if (this.environment.get("DYNAMODB_CONFIG_TABLE") == null) {
            throw new IllegalArgumentException("DYNAMODB_CONFIG_TABLE environment variable is not set.");
        }
    }

    protected Map<String, String> getRuntimeParameters(Map<String, String> parameters) {
        Map<String, String> commandLineParameters = super.getRuntimeParameters(parameters);

        HashMap<String, String> runtimeParameters = new HashMap<String, String>() {{
            putAll(getDagParameters(commandLineParameters.get("dag")));
            putAll(commandLineParameters);
        }};

        return runtimeParameters;
    }

    protected void preRun() {
        setTaskStatus(Status.RUNNING);
    }

    protected String handleSuccess() {
        super.handleSuccess();
        Map<String, String> pluginParameters = null;

        setTaskStatus(Status.FINISHED);

        notifyDagProcessor();

        return "Success";
    }

    protected String handleException(Exception exception) {
        super.handleException(exception);
        Map<String, String> pluginParameters = null;

        setTaskStatus(Status.FAILED);

        notifyDagProcessor();

        exception.printStackTrace();

        return "Failed: " + exception.getMessage();
    }

    protected Map<String, String> getDagTaskParameters() {
        String dag = getDagId();
        String task = getTaskId();
        LOGGER.debug("Getting DAG Task Parameters for " + dag + "__" + task);
        Map<String, String> dagTaskParameters = getDagTaskParametersFromDynamoDb(dag, task);

        overrideRuntimeParameters(dagTaskParameters);

        LOGGER.debug("DAG Task Parameters: " + dagTaskParameters);
        return dagTaskParameters;
    }

    protected Map<String, String> getDagParameters(String dag) {
        Map<String, String> dagParameters = getDagTaskParametersFromDynamoDb(dag, "DAG");

        return dagParameters;
    }

    void setTaskStatus(Status status) {
        try {
            DagState state = getDagStatePlugin();

            state.setTaskStatus(getDagId(), getTaskId(), getExecutionTime(), status);
        } catch (
            ClassNotFoundException |
            NoSuchMethodException |
            InstantiationException |
            IllegalAccessException |
            InvocationTargetException exception
        ) {
            LOGGER.error(
                "Unable to set the status of " + getDagId() +
                " DAG task " + getTaskId() +
                " to Running."
            );

            exception.printStackTrace();
        }
    }

    void notifyTaskProcessor(Task task) {
        String topic = this.runtimeParameters.get("TASK_TOPIC_ARN");
        TaskNotifier notifier = new TaskNotifier(topic);

        notifier.notify(this.getDagId(), this.getTaskId(), this.getExecutionTime());
    }

    void notifyDagProcessor() {
        String topic = this.runtimeParameters.get("DAG_TOPIC_ARN");
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

    protected void overrideRuntimeParameters(Map<String, String> taskParameters) {
        for (String key : taskParameters.keySet().toArray(new String[taskParameters.size()])) {
            if (this.runtimeParameters.containsKey(key)) {
                this.runtimeParameters.put(key, taskParameters.remove(key));
            }
        }
    }

    DagState getDagStatePlugin()
        throws ClassNotFoundException,
               NoSuchMethodException,
               InstantiationException,
               IllegalAccessException,
               InvocationTargetException
    {
        Class stateClass = null;

        if (this.runtimeParameters.containsKey("DAG_STATE_CLASS")) {
            stateClass = PluginImporter.importPlugin(this.runtimeParameters.get("DAG_STATE_CLASS"));
        } else {
            throw new IllegalArgumentException("Missing value for DAG parameter 'DAG_STATE_CLASS'");
        }

        return (DagState) stateClass.getConstructor(new Class[] {Map.class}).newInstance(this.runtimeParameters);
    }
}
