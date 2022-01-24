package datalabs.etl.dag;

import java.lang.reflect.Constructor;
import java.lang.reflect.InvocationTargetException;
import java.util.HashMap;
import java.util.Map;
import java.util.Vector;

import org.apache.logging.log4j.Logger;
import org.apache.logging.log4j.LogManager;

import datalabs.etl.dag.cache.TaskDataCache;
import datalabs.plugin.PluginImporter;
import datalabs.task.TaskWrapper;


public class DAGTaskWrapper extends TaskWrapper {
    Map<TaskDataCache.Direction, Map<String, String>> cacheParameters;
    static final Logger LOGGER = LogManager.getLogger();

    public DAGTaskWrapper(Map<String, String> parameters) {
        super(parameters);

        this.cacheParameters = new HashMap<TaskDataCache.Direction, Map<String, String>>() {{
            put(TaskDataCache.Direction.INPUT, null);
            put(TaskDataCache.Direction.OUTPUT, null);
        }};
    }

    @Override
    protected Map<String, String> getRuntimeParameters(Map<String, String> parameters) {
        String[] runtimeParameterValues = parameters.get("args").split("__", 3);

        return new HashMap<String, String>() {{
            put("dag", runtimeParameterValues[0]);
            put("task", runtimeParameterValues[1]);
            put("execution_time", runtimeParameterValues[2]);
        }};
    }

    @Override
    protected Map<String, String> getTaskParameters() {
        Map<String, String> defaultParameters = this.getDefaultParameters();
        Map<String, String> taskParameters = this.mergeParameters(defaultParameters, this.getDAGTaskParameters());

        taskParameters = this.extractCacheParameters(taskParameters);

        return taskParameters;
    }

    @Override
    protected Vector<byte[]> getTaskInputData(Map<String, String> parameters) {
        Vector<byte[]> inputData = new Vector<byte[]>();

        try {
            TaskDataCache cachePlugin = this.getCachePlugin(TaskDataCache.Direction.INPUT);

            if (cachePlugin != null) {
                inputData = cachePlugin.extractData();
            }
        } catch (Exception exception) {
            LOGGER.error("Unable to extract data from the task input cache.");
        }

        return inputData;
    }

    @Override
    protected String handleException(Exception exception) {
        LOGGER.error("Handling DAG task exception: " + exception.getMessage());

        return null;
    }

    @Override
    protected String handleSuccess() {
        try {
            TaskDataCache cachePlugin = this.getCachePlugin(TaskDataCache.Direction.OUTPUT);

            if (cachePlugin != null) {
                cachePlugin.loadData(this.task.getData());
            }
        } catch (Exception exception) {
            LOGGER.error("Unable to load data into the task output cache.");
        }

        return null;
    }

    protected Map<String, String> getDefaultParameters() {
        Map<String, String> dagParameters = getDefaultParametersFromEnvironment(getDAGID());
        String execution_time = getExecutionTime();

        dagParameters.put("EXECUTION_TIME", execution_time);
        dagParameters.put("CACHE_EXECUTION_TIME", execution_time);

        return dagParameters;
    }

    protected Map<String, String> getDAGTaskParameters() {
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

    Map<String, String> extractCacheParameters(Map<String, String> taskParameters) {
        final TaskDataCache.Direction INPUT = TaskDataCache.Direction.INPUT;
        final TaskDataCache.Direction OUTPUT = TaskDataCache.Direction.OUTPUT;

        this.cacheParameters.put(INPUT, getCacheParameters(taskParameters, INPUT));
        this.cacheParameters.put(OUTPUT, getCacheParameters(taskParameters, OUTPUT));

        for (Map.Entry mapElement : taskParameters.entrySet()) {
            String key = (String) mapElement.getKey();

            if (key.startsWith("CACHE_")) {
                taskParameters.remove(key);
            }
        }

        return taskParameters;
    }

    TaskDataCache getCachePlugin(TaskDataCache.Direction direction)
            throws IllegalAccessException, InstantiationException, InvocationTargetException, NoSuchMethodException,
                   ClassNotFoundException {
        TaskDataCache plugin = null;
        Map<String, String> cacheParameters = this.cacheParameters.get(direction);

        if (cacheParameters.size() > 1) {
            String pluginName = "datalabs.etl.dag.cache.s3.S3TaskTaskDataCache";

            if (cacheParameters.containsKey("CLASS")) {
                pluginName = cacheParameters.remove("CLASS");
            }

            Class pluginClass = PluginImporter.importPlugin(pluginName);

            Constructor pluginConstructor = pluginClass.getConstructor(new Class[] {Map.class});

            plugin = (TaskDataCache) pluginConstructor.newInstance(cacheParameters);
        }

        return plugin;
    }

    protected String getDAGID() {
        return this.runtimeParameters.get("dag").toUpperCase();
    }

    protected String getTaskID() {
        return this.runtimeParameters.get("task").toUpperCase();
    }

    protected String getExecutionTime() {
        return this.runtimeParameters.get("execution_time").toUpperCase();
    }

    static Map<String, String> getDefaultParametersFromEnvironment(String dagID) {
        Map<String, String> parameters;

        try {
            parameters = DAGTaskWrapper.getParameters(new String[] {dagID.toUpperCase()});
        } catch (Exception exception) {  // FIXME: use a more specific exception
            parameters = new HashMap<String, String>();
        }

        return parameters;
    }

    static Map<String, String> getCacheParameters(Map<String, String> taskParameters, TaskDataCache.Direction direction) {
        /* TODO: Port from Python
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

    static Map<String, String> getParameters(String[] branch) {
        /* TODO: Port from Python
        var_tree = VariableTree.from_environment()

        candidate_parameters = var_tree.get_branch_values(branch)

        return {key:value for key, value in candidate_parameters.items() if value is not None}
        */
        return null;
    }
}
