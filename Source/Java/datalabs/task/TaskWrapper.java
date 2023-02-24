package datalabs.task;

import java.lang.reflect.Constructor;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.util.HashMap;
import java.util.Map;
import java.util.ArrayList;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import datalabs.task.TaskResolver;
import datalabs.task.cache.TaskDataCache;
import datalabs.plugin.PluginImporter;


public class TaskWrapper {
    static final Logger LOGGER = LoggerFactory.getLogger(TaskWrapper.class);
    protected Map<TaskDataCache.Direction, Map<String, String>> cacheParameters;
    protected Map<String, String> environment;
    protected Map<String, String> parameters;
    protected Map<String, String> runtimeParameters;
    protected Task task;
    protected ArrayList<byte[]> output;

    public TaskWrapper(Map<String, String> environment, Map<String, String> parameters) {
        this.environment = environment;
        this.parameters = parameters;
        this.cacheParameters = new HashMap<TaskDataCache.Direction, Map<String, String>>() {{
            put(TaskDataCache.Direction.INPUT, null);
            put(TaskDataCache.Direction.OUTPUT, null);
        }};
    }

    public String run() {
        String response;

        try {
            this.runtimeParameters = this.getRuntimeParameters(this.parameters);

            Map<String, String> taskParameters = this.getTaskParameters();

            TaskWrapper.extractCacheParameters(taskParameters, this.cacheParameters);
            LOGGER.debug("Cache Parameters: " + this.cacheParameters);

            ArrayList<byte[]> taskData = this.getTaskInputData(taskParameters);

            Class taskClass = this.getTaskClass();

            this.task = TaskWrapper.createTask(taskClass, taskParameters, taskData);

            this.preRun();

            ArrayList<byte[]> output = this.task.run();

            this.putTaskOutputData(output);

            response = this.handleSuccess();
        } catch (Exception e) {
            response = this.handleException(e);
        }

        return response;
    }

    public Task getTask() {
        return this.task;
    }

    protected Map<String, String> getRuntimeParameters(Map<String, String> parameters) throws TaskException {
        return new HashMap<String, String>();
    }

    protected Map<String, String> getTaskParameters() throws TaskException {
        return this.environment;
    }

    protected ArrayList<byte[]> getTaskInputData(Map<String, String> parameters) throws TaskException {
        ArrayList<byte[]> inputData = new ArrayList<byte[]>();

        try {
            TaskDataCache cachePlugin = this.getCachePlugin(TaskDataCache.Direction.INPUT);

            if (cachePlugin != null) {
                inputData = cachePlugin.extractData();
            }
        } catch (Exception exception) {
            throw new TaskException("Unable to get task input data from cache.", exception);
        }

        return inputData;
    }

    Class getTaskClass() throws TaskException {
        Class taskClass = null;

        try {
            Class taskResolverClass = this.getTaskResolverClass();
            Method getTaskClass = taskResolverClass.getMethod("getTaskClass", new Class[] {Map.class, Map.class});
            LOGGER.debug("Runtime Parameters: " + this.runtimeParameters);
            LOGGER.debug("Task Resolver Class: " + taskResolverClass);

            taskClass = (Class) getTaskClass.invoke(null, this.environment, this.runtimeParameters);
        } catch (Exception exception) {
            throw new TaskException("Unable to resolve task class.", exception);
        }

        return taskClass;
    }

    static Task createTask(Class taskClass, Map<String, String> parameters, ArrayList<byte[]> data)
             throws TaskException {
        Task task = null;

        try {
            task = (Task) taskClass.getConstructor(new Class[] {Map.class, ArrayList.class}).newInstance(
                parameters,
                data
            );
        } catch (Exception exception) {
            throw new TaskException("Unable to create task instance.", exception);
        }

        return task;
    }

    protected void preRun() throws TaskException {
    }

    protected void putTaskOutputData(ArrayList<byte[]> output) throws TaskException {
        TaskDataCache cachePlugin = null;

        try {
            cachePlugin = this.getCachePlugin(TaskDataCache.Direction.OUTPUT);

            if (cachePlugin != null) {
                cachePlugin.loadData(output);
            }
        } catch (Exception exception) {
            throw new TaskException("Unable to load task output data to cache.", exception);
        }
    }

    protected String handleSuccess() throws TaskException {
        return "Success";
    }

    protected String handleException(Exception exception) {
        exception.printStackTrace();

        return exception.getMessage();
    }

    Class getTaskResolverClass() throws ClassNotFoundException {
        String taskResolverClassName = (String) this.environment.getOrDefault(
            "TASK_RESOLVER_CLASS",
            "datalabs.task.EnvironmentTaskResolver"
        );

        return PluginImporter.importPlugin(taskResolverClassName);
    }

    static void extractCacheParameters(
        Map<String, String> taskParameters,
        Map<TaskDataCache.Direction, Map<String, String>> cacheParameters
    ) {
        LOGGER.debug("Task parameters before extraction: " + taskParameters);
        final TaskDataCache.Direction INPUT = TaskDataCache.Direction.INPUT;
        final TaskDataCache.Direction OUTPUT = TaskDataCache.Direction.OUTPUT;

        cacheParameters.put(INPUT, getCacheParameters(taskParameters, INPUT));
        cacheParameters.put(OUTPUT, getCacheParameters(taskParameters, OUTPUT));
        LOGGER.debug("Cache Parameters: " + cacheParameters);

        for (String key : taskParameters.keySet().toArray(new String[taskParameters.size()])) {
            if (key.startsWith("CACHE_")) {
                LOGGER.debug("Removing cache parameter " + key + " from task parameters...");
                taskParameters.remove(key);
            }
        }
        LOGGER.debug("Task parameters after extraction: " + taskParameters);
    }

    static Map<String, String> getCacheParameters(
        Map<String, String> taskParameters,
        TaskDataCache.Direction direction
    ) {
        HashMap<String, String> cacheParameters = new HashMap<String, String>();

        taskParameters.forEach(
            (key, value) -> TaskWrapper.putIfCacheVariable(key, value, direction, cacheParameters)
        );

        return cacheParameters;
    }

    static void putIfCacheVariable(
        String name,
        String value,
        TaskDataCache.Direction direction,
        Map<String, String> cacheParameters
    ) {
        TaskDataCache.Direction otherDirection = TaskDataCache.Direction.INPUT;

        if (direction == TaskDataCache.Direction.INPUT) {
            otherDirection = TaskDataCache.Direction.OUTPUT;
        }

        if (name.startsWith("CACHE_")) {
            Matcher matcher = Pattern.compile("CACHE_" + direction.name() + "_(?<name>..*)").matcher(name);
            Matcher otherMatcher = Pattern.compile("CACHE_" + otherDirection.name() + "_(?<name>..*)").matcher(name);

            if (matcher.find()) {
                cacheParameters.put(matcher.group("name"), value);
            } else if (!otherMatcher.find()) {
                cacheParameters.put(name.substring("CACHE_".length()), value);
            }
        }
    }

    TaskDataCache getCachePlugin(TaskDataCache.Direction direction)
            throws IllegalAccessException, InstantiationException, InvocationTargetException, NoSuchMethodException,
                   ClassNotFoundException {
        TaskDataCache plugin = null;
        Map<String, String> cacheParameters = this.cacheParameters.get(direction);

        if (cacheParameters.size() > 1) {
            String pluginName = null;

            if (cacheParameters.containsKey("CLASS")) {
                pluginName = cacheParameters.remove("CLASS");
            } else {
                throw new ClassNotFoundException("Cache class '" + pluginName + "' not found.");
            }

            Class pluginClass = PluginImporter.importPlugin(pluginName);

            Constructor pluginConstructor = pluginClass.getConstructor(new Class[] {Map.class});

            plugin = (TaskDataCache) pluginConstructor.newInstance(cacheParameters);
        }

        return plugin;
    }
}
