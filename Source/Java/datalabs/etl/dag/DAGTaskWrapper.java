package datalabs.etl.dag;

import datalabs.task.Task;
import datalabs.task.TaskWrapper;


public class DAGTaskWrapper extends TaskWrapper {
    Task task;
    Map<String, String> runtimeParameters;
    Map<String, String> taskParameters;
    Map<String, String> cacheParameters;

    public static void run() {
        String response = null;

        try {
            this.setupEnvironment();

            this._runtimeParameters = this.getRuntimeParameters(this.parameters);

            this.taskParameters = this.getTaskParameters();

            // FIXME
            // this.task = this.task.class(this.taskParameters);

            this.preRun();

            this.task.run();

            response = this.handleSuccess();

        } catch (Exception e) {
            response = this.handleException(e);
        }

        return response;
    }

    public static String setupEnvironment() {
        // TODO: implement
        return null;
    }

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

    public static String getDAGID() {
        return this._runtimeParameters.get("dag").toUpperCase();
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
        return this._runtimeParameters.get("dag").toUpperCase();
    }

    public static String getTaskID() {
        return this._runtimeParameters.get("task").toUpperCase();
    }

    public static String getExecutionTime() {
        return this._runtimeParameters.get("execution_time").toUpperCase();
    }

    public static void _handle_exception(Exception error) {
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
