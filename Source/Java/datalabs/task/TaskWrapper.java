package datalabs.task;

import java.lang.reflect.Constructor;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Date;
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
    /* The base task wrapper where the task parameters are just the task wrapper parameters.
     */
    static final Logger LOGGER = LoggerFactory.getLogger(TaskWrapper.class);
    protected Map<TaskDataCache.Direction, Map<String, String>> cacheParameters;
    protected Map<String, String> environment;
    protected Map<String, String> parameters;
    protected Map<String, String> taskParameters;
    protected Task task;
    protected ArrayList<byte[]> output;

    protected TaskWrapper() { }

    public TaskWrapper(Map<String, String> environment, Map<String, String> parameters) {
        this.environment = environment;
        this.parameters = parameters;
    }

    public String run() {
        String response;

        try {
            this.taskParameters = this.getTaskParameters();
            LOGGER.debug("Task Parameters: " + this.taskParameters);

            this.cacheParameters = extractCacheParameters(this.taskParameters);
            LOGGER.debug("Cache Parameters: " + cacheParameters);

            ArrayList<byte[]> taskData = this.getTaskInputData();

            Class taskClass = this.getTaskClass();

            this.task = TaskWrapper.createTask(taskClass, this.taskParameters, taskData);

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

    protected Map<String, String> getTaskParameters() throws TaskException {
        HashMap<String, String> taskParameters = new HashMap<String, String>(this.parameters);
        String executionTime = this.getExecutionTime();

        taskParameters.putAll(this.environment);

        if (!taskParameters.containsKey("EXECUTION_TIME")) {
            taskParameters.put("EXECUTION_TIME", this.getExecutionTime());
        }

        if (!taskParameters.containsKey("CACHE_EXECUTION_TIME")) {
            taskParameters.put("CACHE_EXECUTION_TIME", this.getExecutionTime());
        }

        return taskParameters;
    }

    protected ArrayList<byte[]> getTaskInputData() throws TaskException {
        ArrayList<byte[]> inputData = new ArrayList<byte[]>();

        try {
            TaskDataCache cachePlugin = TaskWrapper.getCachePlugin(this.cacheParameters.get(TaskDataCache.Direction.INPUT));

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
            LOGGER.debug("Task Resolver Class: " + taskResolverClass);

            taskClass = (Class) getTaskClass.invoke(null, this.environment, this.taskParameters);
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
            cachePlugin = TaskWrapper.getCachePlugin(this.cacheParameters.get(TaskDataCache.Direction.OUTPUT));

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

    static String getExecutionTime() {
        DateFormat formatter = new SimpleDateFormat ("yyyy-MM-dd'T'HH:mm:ss");

        return formatter.format(new Date());
    }

    protected Class getTaskResolverClass() throws ClassNotFoundException {
        String taskResolverClassName = (String) this.environment.getOrDefault(
            "TASK_RESOLVER_CLASS",
            "datalabs.task.EnvironmentTaskResolver"
        );

        return PluginImporter.importPlugin(taskResolverClassName);
    }

    static Map<TaskDataCache.Direction, Map<String, String>> extractCacheParameters(Map<String, String> taskParameters) {
        Map<TaskDataCache.Direction, Map<String, String>> cacheParameters
            = new HashMap<TaskDataCache.Direction, Map<String, String>>() {{
            put(TaskDataCache.Direction.INPUT, getCacheParameters(taskParameters, TaskDataCache.Direction.INPUT));
            put(TaskDataCache.Direction.OUTPUT, getCacheParameters(taskParameters, TaskDataCache.Direction.OUTPUT));
        }};

        return cacheParameters;
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

    static TaskDataCache getCachePlugin(Map<String, String> cacheParameters)
            throws IllegalAccessException, InstantiationException, InvocationTargetException, NoSuchMethodException,
                   ClassNotFoundException {
        TaskDataCache plugin = null;

        if (cacheParameters.size() > 1) {
            String pluginName = cacheParameters.get("CLASS");

            Class pluginClass = PluginImporter.importPlugin(pluginName);

            Constructor pluginConstructor = pluginClass.getConstructor(new Class[] {Map.class});

            plugin = (TaskDataCache) pluginConstructor.newInstance(cacheParameters);
        }

        return plugin;
    }
}
