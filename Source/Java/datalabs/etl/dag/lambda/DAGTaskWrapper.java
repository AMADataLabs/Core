package datalabs.etl.dag.lambda;

import java.util.Map;

import datalabs.task.Task;
import datalabs.task.TaskWrapper;


public class DAGTaskWrapper extends TaskWrapper {
    public static Map<String, String> getRuntimeParameters(Map<String, String> parameters) {
        /* FIXME
        String[] runtime = parameters.get(1).split("__", 3);
        String dag = runtime[0];
        String task = runtime[1];
        String execution_time = runtime[2];

        Map<String, String> runtimeParameters;
        runtimeParameters.put("dag", dag);
        runtimeParameters.put("task", task);
        runtimeParameters.put("execution_time", execution_time);
        */

        return runtimeParameters;
    }

    public static Map<String, String> getTaskParameters(String arg) {
        Map<String, String> defaultParameters = getDefaultParameters();

        Map<String, String> taskParameters = mergeParameters(default_parameters, taskParameters);

        taskParameters = extractCacheParameters(taskParameters);

        // Add Cache Plugin functionality, Python equivalent below:
        //
        // cache_plugin = self._get_cache_plugin(CacheDirection.INPUT)
        // if cache_plugin:
        // input_data = cache_plugin.extract_data()
        //
        // taskParameters['data'] = input_data

        return taskParameters;
    }

    public static Map<String, String> getDefaultParameters() {
        Map<String, String> dagParameters = getDefaultParametersFromEnvironment(getDAGID());
        String execution_time = getExecutionTime();

        dagParameters.put("EXECUTION_TIME", execution_time);
        dagParameters.put("CACHE_EXECUTION_TIME", execution_time);

        return dagParameters;
    }

    public static Map<String, String> extractCacheParameters(Map<String, String> taskParameters) {
        // Uses explicit directions as Strings rather than as a direction object like in Pyton implementation
        this._cacheParameters.put("INPUT", getCacheParameters(this._taskParameters, "INPUT"));
        this._cacheParameters.put("OUTPUT", getCacheParameters(this._taskParameters, "OUTPUT"));

        for (Map.Entry mapElement : taskParameters.entrySet()) {
            String key = mapElement.getKey();
            if (key.startsWith("CACHE_")) {
                taskParameters.remove(key);
            }
        }

        return taskParameters;
    }

    public static Map<String, String> getDefaultParametersFromEnvironment(String dag_id) {
        Map<String, String> parameters;

        try {
            parameters = getParameters(dag_id);
        } catch (Exception e) {
            ;
        }

        return parameters;
    }

    public static Map<String, String> mergeParameters(Map<String, String> parameters, Map<String, String> new_parameters) {
        for (Map.Entry mapElement : parameters.entrySet()) {
            String key = mapElement.getKey();
            if (new_parameters.containsKey(key)) {
                parameters.put(key, new_parameters.get(key));
            }
        }

        return parameters;
    }

    public static String getDAGID() {
        return this.runtimeParameters.get("dag").toUpperCase();
    }

    public static String getTaskID() {
        return this.runtimeParameters.get("task").toUpperCase();
    }

    public static String getExecutionTime() {
        return this.runtimeParameters.get("execution_time").toUpperCase();
    }

    public static void handleException(Exception error) {
        // Need to add Logging message for errors
        String dag = getDAGID();
        String task = getTaskID();

        return "An exception occured while attempting to send a run notification for task " + task + " of DAG " + dag + ".";
    }

    public static String handleSuccess(String arg) {
        // Need to add cache_plugin method functionality
        //
        // cache_plugin = self._get_cache_plugin(CacheDirection.OUTPUT)  # pylint: disable=no-member
        // if cache_plugin:
        // cache_plugin.load_data(self.task.data)
        //
        // LOGGER.info('DAG task has finished')
        return "Success";
    }

    public static String getParameters(String arg) {
        // Need to add functionality
        //
        // var_tree = VariableTree.from_environment()
        // candidate_parameters = var_tree.get_branch_values(branch)
        // return {key:value for key, value in candidate_parameters.items() if value is not None}
    }

    public static Map<String, String> getCacheParameters(Map<String, String> taskParameters, String cache_direction) {
        Map<String, String> cacheParameters;
        String other_direction;

        // Python version uses more complex logic, see: Source/Python/datalabs/etl/dag/task.py
        if (cache_direction == "INPUT") {
            other_direction = "OUTPUT";
        } else {
            other_direction = "INPUT";
        }

        for (Map.Entry mapElement : this._taskParameters.entrySet()) {
            String key = mapElement.getKey();
            String value = mapElement.getValue();
            String prefix = "CACHE_" + cache_direction + "_";
            if (key.startsWith(prefix)) {
                cacheParameters.put(key.split("_", 3)[2], value);
            }
        }

        return cacheParameters;
    }
}



@add_schema(unknowns=True)
@dataclass
class DAGTaskWrapperParameters:
    dag: str
    task: str
    execution_time: str
    unknowns: dict=None


class DAGTaskWrapper(
    DynamoDBTaskParameterGetterMixin,
    ParameterValidatorMixin,
    PluginExecutorMixin,
    datalabs.etl.dag.task.DAGTaskWrapper
):
    PARAMETER_CLASS = DAGTaskWrapperParameters
    DAG_PARAMETERS = None

    @classmethod
    def _get_runtime_parameters(cls, parameters):
        LOGGER.info('Event Parameters: %s', parameters)
        cls.DAG_PARAMETERS = cls._get_dag_task_parameters_from_dynamodb(parameters["dag"], "DAG")

        parameters["dag_class"] = cls.DAG_PARAMETERS["DAG_CLASS"]

        if "task" not in parameters:
            parameters["task"] = "DAG"

        return parameters

    def _pre_run(self):
        super()._pre_run()

        parameters = self._get_task_wrapper_parameters()

        if parameters.task != "DAG":
            state = self._get_plugin(self.DAG_PARAMETERS["DAG_STATE_CLASS"], parameters)

            state.set_task_status(parameters.dag, parameters.task, parameters.execution_time, Status.RUNNING)

    def _handle_success(self) -> (int, dict):
        super()._handle_success()

        parameters = self._get_task_wrapper_parameters()

        if parameters.task == "DAG":
            for task in self.task.triggered_tasks:
                self._notify_task_processor(task)
        else:
            state = self._get_plugin(self.DAG_PARAMETERS["DAG_STATE_CLASS"], parameters)

            success = state.set_task_status(parameters.dag, parameters.task, parameters.execution_time, Status.FINISHED)

            if not success:
                LOGGER.error('Unable to set status of task %s of dag %s to Finished', parameters.task, parameters.dag)

            self._notify_dag_processor()

        return "Success"

    def _handle_exception(self, exception) -> (int, dict):
        super()._handle_exception(exception)

        parameters = self._get_task_wrapper_parameters()

        if parameters.task != "DAG":
            state = self._get_plugin(self.DAG_PARAMETERS["DAG_STATE_CLASS"], parameters)

            success = state.set_task_status(parameters.dag, parameters.task, parameters.execution_time, Status.FAILED)

            if not success:
                LOGGER.error('Unable to set status of task %s of dag %s to Failed', parameters.task, parameters.dag)

            self._notify_dag_processor()

        LOGGER.exception(
            'An exception occured while attempting to run task %s of DAG %s.',
            self._get_task_id(),
            self._get_dag_id()
        )

        return f'Failed: {str(exception)}'

    def _get_dag_task_parameters(self):
        dag = self._get_dag_id()
        task = self._get_task_id()
        LOGGER.debug('Getting DAG Task Parameters for %s__%s...', dag, task)
        dag_task_parameters = self._get_dag_task_parameters_from_dynamodb(dag, task)
        LOGGER.debug('Raw DAG Task Parameters: %s', dag_task_parameters)

        if task == 'DAG':
            dag_task_parameters["dag"] = dag
        elif "LAMBDA_FUNCTION" in dag_task_parameters:
            dag_task_parameters.pop("LAMBDA_FUNCTION")
        LOGGER.debug('Final DAG Task Parameters: %s', dag_task_parameters)

        return dag_task_parameters

    def _get_task_wrapper_parameters(self):
        parameters = self._runtime_parameters
        parameters.update(self.DAG_PARAMETERS)
        parameters = self._get_validated_parameters(parameters)

        return parameters

    def _notify_task_processor(self, task):
        task_topic = self._runtime_parameters["TASK_TOPIC_ARN"]
        notifier = SNSTaskNotifier(task_topic)

        notifier.notify(self._get_dag_id(), task, self._get_execution_time())

    def _notify_dag_processor(self):
        dag_topic = self._runtime_parameters["DAG_TOPIC_ARN"]
        notifier = SNSDAGNotifier(dag_topic)

        notifier.notify(self._get_dag_id(), self._get_execution_time())
