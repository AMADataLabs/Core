package datalabs.task;

import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.util.HashMap;
import java.util.Map;
import java.util.Vector;

import datalabs.access.parameter.ReferenceEnvironmentLoader;
import datalabs.task.TaskResolver;
import datalabs.plugin.PluginImporter;


public abstract class TaskWrapper {
    protected Map<String, String> environment;
    protected Map<String, String> parameters;
    protected Map<String, String> runtimeParameters;
    protected Task task;

    public TaskWrapper(Map<String, String> parameters) {
        this.parameters = parameters;
    }

    public String run() {
        String response;

        try {
            this.setupEnvironment();

            this.runtimeParameters = this.getRuntimeParameters(this.parameters);

            Map<String, String> taskParameters = this.getTaskParameters();

            Vector<byte[]> taskData = this.getTaskInputData(taskParameters);

            Class taskClass = this.getTaskClass(this.runtimeParameters);

            this.task = TaskWrapper.createTask(taskClass, taskParameters, taskData);

            this.preRun();

            this.task.run();

            response = this.handleSuccess();
        } catch (Exception e) {
            response = this.handleException(e);
        }

        return response;
    }

    public Task getTask() {
        return this.task;
    }

    protected void setupEnvironment() {
        ReferenceEnvironmentLoader environmentLoader = ReferenceEnvironmentLoader.fromSystem();
        this.environment = environmentLoader.load();
    }

    protected Map<String, String> getRuntimeParameters(Map<String, String> parameters) {
        return new HashMap<String, String>();
    }

    protected Map<String, String> getTaskParameters() {
        return this.parameters;
    }

    protected Vector<byte[]> getTaskInputData(Map<String, String> parameters) {
        return null;
    }

    Class getTaskClass(Map<String, String> runtimeParameters)
            throws IllegalAccessException, InstantiationException, InvocationTargetException, NoSuchMethodException,
                   ClassNotFoundException {
        Class taskResolverClass = this.getTaskResolverClass();
        Method getTaskClass = taskResolverClass.getMethod("getTaskClass", new Class[] {Map.class, Map.class});

        return (Class) getTaskClass.invoke(null, this.environment, runtimeParameters);
    }

    static Task createTask(Class taskClass, Map<String, String> parameters, Vector<byte[]> data)
            throws IllegalAccessException, InstantiationException, InvocationTargetException, NoSuchMethodException {
        return (Task) taskClass.getConstructor(new Class[] {Map.class, Vector.class}).newInstance(parameters, data);
    }

    protected void preRun() {
    }

    protected abstract String handleSuccess();

    protected abstract String handleException(Exception exception);

    Class getTaskResolverClass() throws ClassNotFoundException {
        String taskResolverClassName = (String) this.environment.getOrDefault(
            "TASK_RESOLVER_CLASS",
            "datalabs.task.EnvironmentTaskResolver"
        );

        return PluginImporter.importPlugin(taskResolverClassName);
    }
}
