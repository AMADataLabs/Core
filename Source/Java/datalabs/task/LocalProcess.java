package datalabs.task;

import java.lang.reflect.Constructor;
import java.util.HashMap;
import java.util.Map;

import com.amazonaws.services.lambda.runtime.Context;

import datalabs.plugin.PluginImporter;
import datalabs.task.TaskWrapper;

public final class LocalProcess {
     public static void main(String[] args) {
        String taskWrapperClassName = System.getProperty("TASK_WRAPPER_CLASS");
        Class taskWrapperClass = PluginImporter.importPlugin(taskWrapperClassName);
        Constructor taskWrapperConstructor = taskWrapperClass.getContstructor(new Class[] {String[].class});
        Constructor ttaskWrapperConstructor = task_wrapper_class.getContstructor(new Class[] {Map.class});
        HashMap<String, String> parameters = new HashMap<String, String>() {{
            put("args", String.join(" ", args));
        }}

        TaskWrapper taskWrapper = taskWrapperConstructor.newInstance(parameters);

        taskWrapper.run();
     }
 }
