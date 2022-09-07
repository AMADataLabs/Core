package datalabs.etl.dag;

import java.lang.reflect.Constructor;
import java.lang.reflect.InvocationTargetException;
import java.util.HashMap;
import java.util.Map;
import java.util.ArrayList;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import datalabs.access.environment.VariableTree;
import datalabs.etl.dag.cache.TaskDataCache;
import datalabs.plugin.PluginImporter;
import datalabs.task.TaskWrapper;


public class DagTaskWrapper extends TaskWrapper {
    static final Logger LOGGER = LoggerFactory.getLogger(DagTaskWrapper.class);
    protected Map<TaskDataCache.Direction, Map<String, String>> cacheParameters;

    public DagTaskWrapper(Map<String, String> environment, Map<String, String> parameters) {
        super(environment, parameters);

        this.cacheParameters = new HashMap<TaskDataCache.Direction, Map<String, String>>() {{
            put(TaskDataCache.Direction.INPUT, null);
            put(TaskDataCache.Direction.OUTPUT, null);
        }};
    }

    @Override
    protected Map<String, String> getRuntimeParameters(Map<String, String> parameters) throws IllegalArgumentException {
        if (!parameters.containsKey("args")) {
            throw new IllegalArgumentException("Missing \"args\" runtime parameter.");
        }
        String[] commandLineArguments = parameters.get("args").split(" ", 2);

        if (commandLineArguments.length != 2) {
            throw new IllegalArgumentException(
                "Expecting two command-line arguments (<executable name>, <DAG run ID>)."
            );
        }
        String[] runtimeParameterValues = commandLineArguments[1].split("__", 3);

        return new HashMap<String, String>() {{
            put("dag", runtimeParameterValues[0]);
            put("task", runtimeParameterValues[1]);
            put("execution_time", runtimeParameterValues[2].replace("T", " "));
        }};
    }

    @Override
    protected Map<String, String> getTaskParameters() {
        Map<String, String> defaultParameters = this.getDefaultParameters();
        Map<String, String> dagTaskParameters = this.getDagTaskParameters();
        Map<String, String> taskParameters = this.mergeParameters(defaultParameters, dagTaskParameters);

        taskParameters = this.extractCacheParameters(taskParameters);
        LOGGER.debug("Task Parameters: " + dagTaskParameters);

        LOGGER.debug("Runtime parameters BEFORE task parameter overrides: " + this.runtimeParameters);
        taskParameters.forEach(
            (key, value) -> overrideParameter(this.runtimeParameters, key, value)
        );
        LOGGER.debug("Runtime parameters AFTER task parameter overrides: " + this.runtimeParameters);

        return taskParameters;
    }

    @Override
    protected ArrayList<byte[]> getTaskInputData(Map<String, String> parameters) {
        ArrayList<byte[]> inputData = new ArrayList<byte[]>();

        try {
            TaskDataCache cachePlugin = this.getCachePlugin(TaskDataCache.Direction.INPUT);

            if (cachePlugin != null) {
                inputData = cachePlugin.extractData();
            }
        } catch (Exception exception) {
            LOGGER.error("Unable to extract data from the task input cache.", exception);
        }

        return inputData;
    }

    @Override
    protected String handleException(Exception exception) {
        LOGGER.error("Handling DAG task exception: " + exception.getMessage());
        exception.printStackTrace();

        return null;
    }

    @Override
    protected String handleSuccess() {
        try {
            TaskDataCache cachePlugin = this.getCachePlugin(TaskDataCache.Direction.OUTPUT);

            if (cachePlugin != null) {
                cachePlugin.loadData(this.output);
            }
        } catch (Exception exception) {
            LOGGER.error("Unable to load data into the task output cache.", exception);
        }

        return null;
    }

    protected Map<String, String> getDefaultParameters() {
        Map<String, String> dagParameters = getDefaultParametersFromEnvironment(getDagId());
        String execution_time = getExecutionTime();

        dagParameters.put("EXECUTION_TIME", execution_time);
        dagParameters.put("CACHE_EXECUTION_TIME", execution_time);

        return dagParameters;
    }

    protected Map<String, String> getDagTaskParameters() {
        return getTaskParametersFromEnvironment(getDagId(), getTaskId());
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

        for (String key : taskParameters.keySet().toArray(new String[taskParameters.size()])) {
            if (key.startsWith("CACHE_")) {
                taskParameters.remove(key);
            }
        }

        return taskParameters;
    }

    void overrideParameter(Map<String, String> parameters, String key, String value) {
        if (parameters.containsKey(key)) {
            parameters.put(key, value);
        }
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

    protected String getDagId() {
        return this.runtimeParameters.get("dag").toUpperCase();
    }

    protected String getTaskId() {
        return this.runtimeParameters.get("task").toUpperCase();
    }

    protected String getExecutionTime() {
        return this.runtimeParameters.get("execution_time").toUpperCase();
    }

    static Map<String, String> getDefaultParametersFromEnvironment(String dagID) {
        Map<String, String> parameters;

        try {
            parameters = DagTaskWrapper.getParameters(new String[] {dagID.toUpperCase()});
        } catch (Exception exception) {  // FIXME: use a more specific exception
            parameters = new HashMap<String, String>();
        }

        return parameters;
    }

    static Map<String, String> getTaskParametersFromEnvironment(String dagID, String taskID) {
        Map<String, String> parameters;

        try {
            parameters = DagTaskWrapper.getParameters(new String[] {dagID.toUpperCase(), taskID.toUpperCase()});
        } catch (Exception exception) {  // FIXME: use a more specific exception
            parameters = new HashMap<String, String>();
        }

        return parameters;
    }

    static Map<String, String> getCacheParameters(
        Map<String, String> taskParameters,
        TaskDataCache.Direction direction
    ) {
        HashMap<String, String> cacheParameters = new HashMap<String, String>();
        TaskDataCache.Direction otherDirection = TaskDataCache.Direction.INPUT;

        if (direction == TaskDataCache.Direction.INPUT) {
            otherDirection = TaskDataCache.Direction.OUTPUT;
        }

        taskParameters.forEach(
            (key, value) -> DagTaskWrapper.putIfCacheVariable(key, value, direction, cacheParameters)
        );

        return cacheParameters;
    }

    static Map<String, String> getParameters(String[] branch) {
        VariableTree variableTree = VariableTree.fromEnvironment();

        Map<String, String> parameters = variableTree.getBranchValues(branch);
        LOGGER.debug("Branch Values: " + parameters);

        if (parameters == null) {
            parameters = new HashMap<String, String>();
        }
        LOGGER.debug("Environment Parameters: " + parameters);

        return parameters;
    }

    static void putIfCacheVariable(
        String name,
        String value,
        TaskDataCache.Direction direction,
        Map<String, String> cacheParameters
    ) {
        Matcher matcher = Pattern.compile("CACHE_" + direction.name() + "_(?<name>..*)").matcher(name);

        if (matcher.find()) {
            cacheParameters.put(matcher.group("name"), value);
        }
    }
}
