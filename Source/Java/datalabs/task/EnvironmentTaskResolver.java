package datalabs.task;

import java.util.Map;

import datalabs.plugin.PluginImporter;


public class EnvironmentTaskResolver {
    public Class getTaskClass(Map<String, String> parameters) throws ClassNotFoundException {
        String taskClassName = System.getProperty("TASK_RESOLVER_CLASS");

        if (taskClassName == null) {
            throw new IllegalArgumentException("The environment variable \"TASK_RESOLVER_CLASS\" is not set.");
        }

        return PluginImporter.importPlugin(taskClassName);
    }
}
