package datalabs.task;

import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.util.HashMap;
import java.util.Map;
import java.util.ArrayList;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import datalabs.task.TaskResolver;
import datalabs.plugin.PluginImporter;


public class TaskWrapper {
    static final Logger LOGGER = LoggerFactory.getLogger(TaskWrapper.class);
    protected Map<String, String> environment;
    protected Map<String, String> parameters;
    protected Map<String, String> runtimeParameters;
    protected Task task;
    protected ArrayList<byte[]> output;

    public TaskWrapper(Map<String, String> environment, Map<String, String> parameters) {
        this.environment = environment;
        this.parameters = parameters;
    }

    public String run() {
        String response;

        try {
            this.runtimeParameters = this.getRuntimeParameters(this.parameters);

            Map<String, String> taskParameters = this.getTaskParameters();

            ArrayList<byte[]> taskData = this.getTaskInputData(taskParameters);

            Class taskClass = this.getTaskClass();

            this.task = TaskWrapper.createTask(taskClass, taskParameters, taskData);

            this.preRun();

            this.output = this.task.run();

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
        return new ArrayList<byte[]>();
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
}
