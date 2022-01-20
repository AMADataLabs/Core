package datalabs.etl.dag;

import java.util.HashMap;

import software.amazon.awssdk.Parameter_Class;

public class Task {
    HashMap<String, String> _parameters;
    Parameter_Class _parameter_class = null;

    public Task(HashMap<String, String> parameter) {
        this._parameters = parameter;

        if (this._parameter_class != null) {
            // Need to add parameter validation
            ;
        }
    }

    public static String run() {
        ;
    }
}

public class DAGTaskWrapper {
    Task task;
    Task task_class;
    HashMap<String, String> _parameters;
    HashMap<String, String> _runtime_parameters;
    HashMap<String, String> _task_parameters;
    HashMap<String, String> _cache_parameters;


    public DAGTaskWrapper(HashMap<String, String> parameter) {
        this._parameters = parameter;
        // Need to add parameter validation
    }

    public static String run() {
        String response = null;

        try {
            this._setup_environment();

            this._runtime_parameters = this._get_runtime_parameters(this._parameters);

            this._task_parameters = this._get_task_parameters();

            this.task = this.task_class(this._task_parameters);

            this._pre_run();

            this.task.run();

            response = this._handle_success();

        } catch (Exception e) {
            response = this._handle_exception(e);
        }

        return response;
    }

    public static String _setup_environment() {
        // Need to add funcitonality
        return null;
    }

    public static HashMap<String, String> _get_runtime_parameters(HashMap parameters) {
        String[] runtime = parameters.get(1).split("__", 3);
        String dag = runtime[0];
        String task = runtime[1];
        String execution_time = runtime[2];

        HashMap<String, String> runtime_parameters;
        runtime_parameters.put("dag", dag);
        runtime_parameters.put("task", task);
        runtime_parameters.put("execution_time", execution_time);

        return runtime_parameters;
    }

    public static HashMap<String, String> _get_task_parameters(String arg) {
        HashMap<String, String> task_parameters, default_parameters;

        default_parameters = _get_default_parameters();

        task_parameters = _merge_parameters(default_parameters, task_parameters);

        task_parameters = _extract_cache_parameters(task_parameters);

        // Add Cache Plugin functionality, Python equivalent below:
        //
        // cache_plugin = self._get_cache_plugin(CacheDirection.INPUT)
        // if cache_plugin:
        // input_data = cache_plugin.extract_data()
        //
        // task_parameters['data'] = input_data

        return task_parameters;
    }

    public static HashMap<String, String> _get_default_parameters() {
        HashMap<String, String> dag_parameters = _get_default_parameters_from_environment(_get_dag_id());
        String execution_time = _get_execution_time();

        dag_parameters.put("EXECUTION_TIME", execution_time);
        dag_parameters.put("CACHE_EXECUTION_TIME", execution_time);

        return dag_parameters;
    }

    public static HashMap<String, String> _extract_cache_parameters(HashMap<String, String> task_parameters) {
        // Uses explicit directions as Strings rather than as a direction object like in Pyton implementation
        this._cache_parameters.put("INPUT", _get_cache_parameters(this._task_parameters, "INPUT"));
        this._cache_parameters.put("OUTPUT", _get_cache_parameters(this._task_parameters, "OUTPUT"));

        for (Map.Entry mapElement : task_parameters.entrySet()) {
            String key = mapElement.getKey();
            if (key.startsWith("CACHE_")) {
                task_parameters.remove(key);
            }
        }

        return task_parameters;
    }

    public static String _get_dag_id() {
        return this._runtime_parameters.get("dag").toUpperCase();
    }

    public static HashMap<String, String> _get_default_parameters_from_environment(String dag_id) {
        HashMap<String, String> parameters;

        try {
            parameters = _get_parameters(dag_id);
        } catch (Exception e) {
            ;
        }

        return parameters;
    }

    public static HashMap<String, String> _merge_parameters(HashMap<String, String> parameters, HashMap<String, String> new_parameters) {
        for (Map.Entry mapElement : parameters.entrySet()) {
            String key = mapElement.getKey();
            if (new_parameters.containsKey(key)) {
                parameters.put(key, new_parameters.get(key));
            }
        }

        return parameters;
    }

    public static String _get_dag_id() {
        return this._runtime_parameters.get("dag").toUpperCase();
    }

    public static String _get_task_id() {
        return this._runtime_parameters.get("task").toUpperCase();
    }

    public static String _get_execution_time() {
        return this._runtime_parameters.get("execution_time").toUpperCase();
    }

    public static void _handle_exception(Exception error) {
        // Need to add Logging message for errors
        String dag = _get_dag_id();
        String task = _get_task_id();

        return "An exception occured while attempting to send a run notification for task " + task + " of DAG " + dag + ".";
    }

    public static String _handle_success(String arg) {
        // Need to add cache_plugin method functionality
        //
        // cache_plugin = self._get_cache_plugin(CacheDirection.OUTPUT)  # pylint: disable=no-member
        // if cache_plugin:
        // cache_plugin.load_data(self.task.data)
        //
        // LOGGER.info('DAG task has finished')
        return "Success";
    }

    public static String _get_parameters(String arg) {
        // Need to add functionality
        //
        // var_tree = VariableTree.from_environment()
        // candidate_parameters = var_tree.get_branch_values(branch)
        // return {key:value for key, value in candidate_parameters.items() if value is not None}
    }

    public static HashMap<String, String> _get_cache_parameters(HashMap<String, String> task_parameters, String cache_direction) {
        HashMap<String, String> cache_parameters;
        String other_direction;

        // Python version uses more complex logic, see: Source/Python/datalabs/etl/dag/task.py
        if (cache_direction == "INPUT") {
            other_direction = "OUTPUT";
        } else {
            other_direction = "INPUT";
        }

        for (Map.Entry mapElement : this._task_parameters.entrySet()) {
            String key = mapElement.getKey();
            String value = mapElement.getValue();
            String prefix = "CACHE_" + cache_direction + "_";
            if (key.startsWith(prefix)) {
                cache_parameters.put(key.split("_", 3)[2], value);
            }
        }

        return cache_parameters;
    }
}
