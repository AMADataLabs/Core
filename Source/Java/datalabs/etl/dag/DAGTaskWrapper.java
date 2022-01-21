package datalabs.etl.dag;

import org.apache.logging.log4j.Logger;
import org.apache.logging.log4j.LogManager;

import datalabs.plugin.PluginImporter;
import datalabs.etl.task.TaskWrapper;
import datalabs.etl.dag.cache.TaskDataCache;

public static class DAGTaskWrapper extends TaskWrapper {
    Map<TaskDataCache.Direction, Map<String, String>> cacheParameters;
    static final Logger LOGGER = LogManager.getLogger();

    @overrides
    public DAGTaskWrapper(Map<String, String> parameters) {
        super(parameters)

        this.cacheParameters = new Map<TaskDataCache.Direction, Map<String, String>>() {{
            put(TaskDataCache.Direction.INPUT, null);
            put(TaskDataCache.Direction.OUTPUT, null);
        }};
    }

    @overrides
    Map<String, String> getRuntimeParameters(Map<String, String> parameters) {
        String[] runtimeParameterValues = parameters["args"].split("__");

        return new Map<String, String>() {{
            put("dag", runtimeParameterValues[0]);
            put("task", runtimeParameterValues[1]);
            put("execution_time", runtimeParameterValues[2]);
        }}
    }

    @overrides
    Map<String, String> getTaskParameters() {
        Map<String, String> defaultParameters = this.getDefaultParameters();
        Map<String, String> dagTaskParameters = this.getDagTaskParameters();
        Map<String, String> taskParameters = this.mergeParameters(defaultParameters, this.getDagTaskParameters());

        taskParameters = this.extractCacheParameters(taskParameters);

        return taskParameters;
    }

    @overrides
    Vector<byte[]> getTaskInputData(Map<String, String> parameters) {
        Vector<byte[]> inputData = new Vector<byte[]>();
        TaskDataCache cachePlugin = this.getCachePlugin(TaskDataCache.Direction.INPUT);

        if (cachePlugin != null) {
            inputData = cachePlugin.extractData();
        }

        return inputData;
    }

    String handleException(Exception exception) {
        LOGGER.error("Handling DAG task exception: " + exception.getMessage());

        return null;
    }

    String handleSuccess() {
        TaskDataCache cachePlugin = this.getCachePlugin(TaskDataCache.Direction.OUTPUT);

        if (cachePlugin != null) {
            cachePlugin.loadData(this.task.getData());
        }

        return null;
    }

    Map<String, String> getDefaultParameters() {
        /* TODO: port from Python
        dag_parameters = self._get_default_parameters_from_environment(self._get_dag_id())
        execution_time = self._get_execution_time()

        dag_parameters['EXECUTION_TIME'] = execution_time
        dag_parameters['CACHE_EXECUTION_TIME'] = execution_time

        return dag_parameters
        */

        return null;
    }

    Map<String, String> getDAGTaskParameters() {
        /* TODO: port from Python
        return self._get_task_parameters_from_environment(self._get_dag_id(), self._get_task_id())
        */
        return null;
    }

    Map<String, String> mergeParameters(Map<String, String> parameters, Map<String, String>  newParameters) {
        Map<String, String> mergedParameters = new HashMap<>(parameters);

        newParameters.forEach(
            (key, value) -> mergedParameters.merge(key, value, (oldValue, newValue) -> newValue)
        );

        return mergedParameters;
    }

    static Map<String, String> extractCacheParameters(Map<String, String> parameters) {
        /* TODO: port from Python
        self._cache_parameters[CacheDirection.INPUT] = self._get_cache_parameters(
            task_parameters,
            CacheDirection.INPUT
        )
        self._cache_parameters[CacheDirection.OUTPUT] = self._get_cache_parameters(
            task_parameters,
            CacheDirection.OUTPUT
        )
        cache_keys = [key for key in task_parameters if key.startswith('CACHE_')]

        for key in cache_keys:
            task_parameters.pop(key)

        return task_parameters
        */
        return null
    }

    TaskDataCache getCachePlugin(TaskDataCache.Direction direction) {
        TaskDataCache plugin = null;
        Map<String, String> cacheParameters = this.cacheParameters[direction];

        if (cacheParameters.size() > 1): {
            String pluginName = "datalabs.etl.dag.cache.s3.S3TaskTaskDataCache";

            if (cacheParameters.containsKey("CLASS")) {
                pluginName = cacheParameters.remove("CLASS");
            }

            Class pluginClass = PluginImporter.importPlugin(pluginName);

            plugin = pluginClass.getConstructor(new Class[] {Map<String, String>}).newInstance([cacheParameters]);
        }

        return plugin
    }

    String getDAGID() {
        return this.runtimeParameters["dag"];
    }

    String getTaskID() {
        return this.runtimeParameters["task"];
    }

    String getExecutionTime() {
        return this.runtimeParameters["execution_time"];
    }

    static Map<String, String> getDefaultParametersFromEnvironment(String dagID) {
        Map<String, String> parameters;

        try {
            parameters = DAGTaskWrapper.getParameters([dagID.toUpperCase()])
        } catch (Exception exception) {  // FIXME: use a more specific exception
            parameters = new HashMap<String, String>();
        }

        return parameters;
    }

    static Map<String, String> getgetCacheParameters(Map<String, String> taskParameters, TaskDataCache.Direction direction) {
        /* Port from Python
        cache_parameters = {}
        other_direction = [d[1] for d in CacheDirection.__members__.items() if d[1] != direction][0]  # pylint: disable=no-member

        for key, value in task_parameters.items():
            match = re.match(f'CACHE_({direction.value}_)?(..*)', key)

            if match and not match.group(2).startswith(other_direction.value+'_'):
                cache_parameters[match.group(2)] = value

        return cache_parameters
        */
        return null;
    }

    static Map<String, String> getParameters(String branch) {
        /* Port from Python
        var_tree = VariableTree.from_environment()

        candidate_parameters = var_tree.get_branch_values(branch)

        return {key:value for key, value in candidate_parameters.items() if value is not None}
        */
    }
}
