package datalabs.task;

import java.lang.reflect.Constructor;
import java.lang.reflect.InvocationTargetException;
import java.util.HashMap;
import java.util.Map;

import com.amazonaws.services.lambda.runtime.Context;

import datalabs.plugin.PluginImporter;
import datalabs.task.TaskWrapper;

public class LocalProcess {
     public static void main(String[] args)
            throws IllegalAccessException, InstantiationException, InvocationTargetException, NoSuchMethodException,
                   ClassNotFoundException {
        String taskWrapperClassName = System.getProperty("TASK_WRAPPER_CLASS");
        Class taskWrapperClass = PluginImporter.importPlugin(taskWrapperClassName);
        Constructor taskWrapperConstructor = taskWrapperClass.getConstructor(new Class[] {String[].class});
        HashMap<String, String> parameters = new HashMap<String, String>() {{
            put("args", String.join(" ", args));
        }};

        TaskWrapper taskWrapper = (TaskWrapper) taskWrapperConstructor.newInstance(parameters);

        taskWrapper.run();
     }
 }
