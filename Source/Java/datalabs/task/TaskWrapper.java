package datalabs.task;

import java.util.Map;

import datalabs.plugin.PluginImporter;


public abstract class TaskWrapper {
    Map<String, String> parameters;
    Map<String, String> runtimeParameters;
    Map<String, String> taskParameters;
    Map<String, String> cacheParameters;
    Class taskClass;
    Task task;

    public TaskWrapper(Map<String, String> parameters) {
        this.parameters = parameters;
    }

    public static String run() {
        String response;

        try {
            this.setupEnvironment();

            this._runtimeParameters = this.getRuntimeParameters(this.parameters);

            this.taskParameters = this.getTaskParameters();

            this.taskData = this.getTaskData(this.taskParameters)

            this.taskClass = this.getTaskClass();

            this.task = TaskWrapper.createTask(this.taskClass, this.taskParameters, this.taskData)

            this.preRun();

            this.task.run();

            response = this.handleSuccess();

        } catch (Exception e) {
            response = this.handleException(e);
        }

        return response
    }

    void setupEnvironment() {
        /* TODO: implement ReferenceEnvironmentLoader
        environmentLoader = ReferenceEnvironmentLoader.fromEnviron()
        environmentLoader.load()
        */
    }

    Map<String, String> getRuntimeParameters(Map<String, String> parameters) {
        return new Map<String, String>();
    }

    Map<String, String> getTaskParameters() {
        return this._parameters;
    }

    Vector<byte[]> getTaskInputData(Map<String, String> parameters) {
        return null;
    }

    Class getTaskClass() {
        taskResolverClass = this.getTaskResolverClass();

        taskClass = taskResolverClass.getTaskClass(this.runtimeParameters);

        return taskClass
    }

    static Task createTask(Class taskClass, Map<String, String> parameters) {
        return taskClass.getConstructor(new Class[] {Map<String, String>, byte[][]}).newInstance([taskParameters]);
    }

    void preRun() {
    }

    abstract String handleSuccess() {
    }

    abstract String handleException() {
    }

    Class getTaskResolverClass() {
        taskResolverClassName = System.getProperty("TASK_RESOLVER_CLASS", "datalabs.task.EnvironmentTaskResolver");
        Class taskResolverClass = PluginImporter.importPlugin(taskResolverClassName);

        return taskResolverClass
    }
}
