package datalabs.etl.dag.lambda;

import java.lang.reflect.InvocationTargetException;
import java.util.HashMap;
import java.util.Map;
import java.util.Vector;

import org.apache.logging.log4j.Logger;
import org.apache.logging.log4j.LogManager;

import datalabs.access.parameter.DynamoDbEnvironmentLoader;
import datalabs.etl.dag.state.DagState;
import datalabs.etl.dag.state.Status;
import datalabs.plugin.PluginImporter;
import datalabs.task.Task;


public class DagTaskWrapper extends datalabs.etl.dag.DagTaskWrapper {
    static final Logger LOGGER = LogManager.getLogger();
    Map<String, String> taskParameters;

    public DagTaskWrapper(Map<String, String> parameters) {
        super(parameters);
    }

    protected Map<String, String> getRuntimeParameters(Map<String, String> parameters) {
        if ("DAG".equals(parameters.get("type"))) {
            throw new UnsupportedOperationException("DAG processing is not supported in Java.");
        }

        HashMap<String, String> runtimeParameters = new HashMap<String, String>() {{
            putAll(getDagParameters(parameters));
            putAll(parameters);
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
        LOGGER.debug("DAG Task Parameters: " + dagTaskParameters);

        return dagTaskParameters;
    }

    protected Map<String, String> getDagParameters(Map<String, String> taskWrapperParameters) {
        Map<String, String> dagParameters = getDagTaskParametersFromDynamoDb(taskWrapperParameters.get("dag"), "DAG");

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
        // task_topic = self._runtime_parameters["TASK_TOPIC_ARN"]
        // notifier = SNSTaskNotifier(task_topic)
        //
        // notifier.notify(self._get_dag_id(), task, self._get_execution_time())
    }

    void notifyDagProcessor() {
        // dag_topic = self._runtime_parameters["DAG_TOPIC_ARN"]
        // notifier = SNSDAGNotifier(dag_topic)
        //
        // notifier.notify(self._get_dag_id(), self._get_execution_time())
    }

    protected Map<String, String> getDagTaskParametersFromDynamoDb(String dag, String task) {
        HashMap<String, String> parameters = new HashMap<String, String>();

        DynamoDbEnvironmentLoader loader = new DynamoDbEnvironmentLoader(
            this.environment.get("DYNAMODB_CONFIG_TABLE"),
            dag,
            task
        );

        return loader.load(parameters);
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
