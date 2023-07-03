package datalabs.task;

import java.util.Map;

import datalabs.plugin.PluginImporter;


public class RuntimeTaskResolver {
    public static Class getTaskClass(Map<String, String>  environment, Map<String, String> taskParameters)
            throws ClassNotFoundException {
        String taskClassName = taskParameters.get("TASK_CLASS");

        if (taskClassName == null) {
            throw new IllegalArgumentException("The runtime parameter \"TASK_CLASS\" is not set.");
        }

        return PluginImporter.importPlugin(taskClassName);
    }
}
