package datalabs.etl.dag.lambda;

import java.lang.reflect.InvocationTargetException;
import java.util.HashMap;
import java.util.Map;
import java.util.Vector;

import datalabs.access.parameter.DynamoDbEnvironmentLoader;
import datalabs.etl.dag.state.DagState;
import datalabs.etl.dag.state.Status;
import datalabs.parameter.Parameters;
import datalabs.plugin.PluginImporter;
import datalabs.task.Task;


class DagTaskWrapperParameters extends Parameters {
    public String dag;
    public String task;
    public String executionTime;
    public Map<String, String> unknowns;

    DagTaskWrapperParameters(Map<String, String> parameters) throws IllegalAccessException, IllegalArgumentException {
        super(parameters);
    }
}


public class DagTaskWrapper extends datalabs.etl.dag.DagTaskWrapper {
    Map<String, String> dagParameters = null;

    public DagTaskWrapper(Map<String, String> parameters) {
        super(parameters);
    }

    protected Map<String, String> getRuntimeParameters(Map<String, String> parameters) {
        this.dagParameters = getDagTaskParametersFromDynamoDb(parameters.get("dag"), "DAG");
        HashMap<String, String> runtimeParameters = new HashMap<String, String>() {{
            putAll(parameters);
        }};

        runtimeParameters.put("dag_class", dagParameters.get("DAG_CLASS"));

        if (!parameters.containsKey("task")) {
            throw new UnsupportedOperationException("DAG processing is not supported in Java.");
        }

        return runtimeParameters;
    }

    protected void preRun() {
        DagTaskWrapperParameters parameters = null;

        try {
            parameters = getTaskWrapperParameters();
        } catch (IllegalAccessException | IllegalArgumentException exception) {
                LOGGER.error("Unable to get TaskWrapper parameters.");
                exception.printStackTrace();
        }

        if (parameters.task != "DAG") {
            try {
                setTaskStatus(parameters, Status.RUNNING);
            } catch (
                ClassNotFoundException |
                NoSuchMethodException |
                InstantiationException |
                IllegalAccessException |
                InvocationTargetException exception
            ) {
                LOGGER.error(
                    "Unable to set the status of " + parameters.dag +
                    " DAG task " + parameters.task +
                    " to Running."
                );
            }
        }
    }

    void setTaskStatus(DagTaskWrapperParameters parameters, Status status)
        throws ClassNotFoundException,
               NoSuchMethodException,
               InstantiationException,
               IllegalAccessException,
               InvocationTargetException
    {
        DagState state = getDagStatePlugin(parameters);

        state.setTaskStatus(parameters.dag, parameters.task, parameters.executionTime, status);
    }

    protected String handleSuccess() {
        super.handleSuccess();
        DagTaskWrapperParameters parameters = null;

        try {
            parameters = getTaskWrapperParameters();
        } catch (IllegalAccessException | IllegalArgumentException exception) {
                LOGGER.error("Unable to get TaskWrapper parameters.");
                exception.printStackTrace();
        }

        try {
            DagState state = getDagStatePlugin(parameters);

            state.setTaskStatus(parameters.dag, parameters.task, parameters.executionTime, Status.FINISHED);
        } catch (Exception exception) {
            LOGGER.error(
                "Unable to set status of task " + parameters.task + " of dag " + parameters.dag + " to Finished"
            );
        }

        notifyDagProcessor();

        return "Success";
    }

    protected String handleException(Exception exception) {
        super.handleException(exception);
        DagTaskWrapperParameters parameters = null;

        try {
            parameters = getTaskWrapperParameters();
        } catch (IllegalAccessException | IllegalArgumentException secondaryException) {
            LOGGER.error("Unable to get TaskWrapper parameters.");
            secondaryException.printStackTrace();
        }

        try {
            DagState state = getDagStatePlugin(parameters);

            state.setTaskStatus(parameters.dag, parameters.task, parameters.executionTime, Status.FAILED);
        } catch (Exception secondaryException) {
            LOGGER.error(
                "Unable to set status of task " + parameters.task + " of dag " + parameters.dag + " to Failed"
            );
            secondaryException.printStackTrace();
        }

        notifyDagProcessor();

        exception.printStackTrace();

        return "Failed: " + exception.getMessage();
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

    DagTaskWrapperParameters getTaskWrapperParameters() throws IllegalAccessException, IllegalArgumentException {
        Map<String, String> runtimeParameters = this.runtimeParameters;
        Map<String, String> dagParameters = this.dagParameters;
        HashMap<String, String> parameters = new HashMap<String, String>() {{
            putAll(runtimeParameters);
            putAll(dagParameters);
        }};

        return new DagTaskWrapperParameters(parameters);
    }

    DagState getDagStatePlugin(DagTaskWrapperParameters parameters)
        throws ClassNotFoundException,
               NoSuchMethodException,
               InstantiationException,
               IllegalAccessException,
               InvocationTargetException
    {
        Class stateClass = PluginImporter.importPlugin(this.dagParameters.get("DAG_STATE_CLASS"));

        return (DagState) stateClass.getConstructor(new Class[] {Map.class, Vector.class}).newInstance(
            parameters
        );
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

    protected Map<String, String> getDagTaskParameters() {
        // dag = self._get_dag_id()
        // task = self._get_task_id()
        // LOGGER.debug('Getting DAG Task Parameters for %s__%s...', dag, task)
        // dag_task_parameters = self._get_dag_task_parameters_from_dynamodb(dag, task)
        // LOGGER.debug('Raw DAG Task Parameters: %s', dag_task_parameters)
        //
        // if task == 'DAG':
        //     dag_task_parameters["dag"] = dag
        // elif "LAMBDA_FUNCTION" in dag_task_parameters:
        //     dag_task_parameters.pop("LAMBDA_FUNCTION")
        // LOGGER.debug('Final DAG Task Parameters: %s', dag_task_parameters)
        //
        // return dag_task_parameters

        return null;
    }
}
