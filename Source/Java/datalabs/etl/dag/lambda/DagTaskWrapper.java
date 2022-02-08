package datalabs.etl.dag.lambda;

import java.util.HashMap;
import java.util.Map;

import datalabs.access.parameter.DynamoDbEnvironmentLoader;
import datalabs.etl.dag.state.Status;
import datalabs.parameter.Parameters;
import datalabs.plugin.PluginImporter;
import datalabs.task.Task;


class DagTaskWrapperParameters extends Parameters {
    public String dag;
    public String task;
    public String executionTime;
    public Map<String, String> unknowns;
}


public class DagTaskWrapper extends datalabs.etl.dag.DagTaskWrapper {
    Map<String, String> dagParameters = null;

    public DagTaskWrapper(Map<String, String> parameters) {
        super(parameters);
    }

    protected Map<String, String> getRuntimeParameters(Map<String, String> parameters) {
        this.dagParameters = getDagTaskParametersFromDynamoDB(parameters.getOrDefault("dag"), "DAG");
        HashMap<String, String> runtimeParameters = new HashMap<String, String>() {{
            putAll(parameters);
        }};

        runtimeParameters.put("dag_class", dagParameters.get("DAG_CLASS"));

        if (!parameters.containsKey("task")) {
            runtimeParameters.put("task", "DAG");
        }
    }

    protected void preRun() {
        DagTaskWrapperParameters parameters = getTaskWrapperParameters();

        if (parameters.task != "DAG") {
            setTaskStatus(parameters, Status.RUNNING);
        }
        // super()._pre_run()
        //
        // parameters = self._get_task_wrapper_parameters()
        //
        // if parameters.task != "DAG":
        //     state = self._get_plugin(self.DAG_PARAMETERS["DAG_STATE_CLASS"], parameters)
        //
        //     state.set_task_status(parameters.dag, parameters.task, parameters.execution_time, Status.RUNNING)
    }

    static void setTaskStatus(Map<String, String> parameters, Status status) throws ClassNotFoundException {
        Class stateClass = PluginImporter.importPlugin(this.dagParameters.get("DAG_STATE_CLASS"));
        DagState state = (DagState) taskClass.getConstructor(new Class[] {Map.class, Vector.class}).newInstance(
            parameters
        );

        state.setTaskStatus(parameters.dag, parameters.task, parameters.executionTime, status);
    }

    protected String handleSuccess() {
        // super()._handle_success()
        //
        // parameters = self._get_task_wrapper_parameters()
        //
        // if parameters.task == "DAG":
        //     for task in self.task.triggered_tasks:
        //         self._notify_task_processor(task)
        // else:
        //     state = self._get_plugin(self.DAG_PARAMETERS["DAG_STATE_CLASS"], parameters)
        //
        //     success = state.set_task_status(parameters.dag, parameters.task, parameters.execution_time, Status.FINISHED)
        //
        //     if not success:
        //         LOGGER.error('Unable to set status of task %s of dag %s to Finished', parameters.task, parameters.dag)
        //
        //     self._notify_dag_processor()
        //
        // return "Success"

        return null;
    }

    protected String handleException(Exception exception) {
        // super()._handle_exception(exception)
        //
        // parameters = self._get_task_wrapper_parameters()
        //
        // if parameters.task != "DAG":
        //     state = self._get_plugin(self.DAG_PARAMETERS["DAG_STATE_CLASS"], parameters)
        //
        //     success = state.set_task_status(parameters.dag, parameters.task, parameters.execution_time, Status.FAILED)
        //
        //     if not success:
        //         LOGGER.error('Unable to set status of task %s of dag %s to Failed', parameters.task, parameters.dag)
        //
        //     self._notify_dag_processor()
        //
        // LOGGER.exception(
        //     'An exception occured while attempting to run task %s of DAG %s.',
        //     self._get_task_id(),
        //     self._get_dag_id()
        // )
        //
        // return f'Failed: {str(exception)}'
        return null;
    }

    protected Map<String, String> getDagTaskParametersFromDynamoDB(String dag, String task) {
        HashMap<String, String> parameters = new HashMap<String, String>();

        DynamoDbEnvironmentLoader loader = DynamoDbEnvironmentLoader(
            this.environment.get("DYNAMODB_CONFIG_TABLE"),
            dag,
            task
        );

        return loader.load(parameters);
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

    DagTaskWrapperParameters getTaskWrapperParameters() {
        HashMap<String, String> parameters = new HashMap<String, String>() {{
            putAll(this.runtimeParameters);
            putAll(this.dagParameters);
        }};

        return new DagTaskWrapperParameters(parameters);
    }

    void notifyTaskProcessor(Task task) {
        // task_topic = self._runtime_parameters["TASK_TOPIC_ARN"]
        // notifier = SNSTaskNotifier(task_topic)
        //
        // notifier.notify(self._get_dag_id(), task, self._get_execution_time())
    }

    void notifyDAGProcessor() {
        // dag_topic = self._runtime_parameters["DAG_TOPIC_ARN"]
        // notifier = SNSDAGNotifier(dag_topic)
        //
        // notifier.notify(self._get_dag_id(), self._get_execution_time())
    }
}
