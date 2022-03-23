package datalabs.task;

import java.lang.reflect.Constructor;
import java.lang.reflect.InvocationTargetException;
import java.util.HashMap;
import java.util.Map;

import com.amazonaws.services.lambda.runtime.Context;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import datalabs.plugin.PluginImporter;
import datalabs.task.TaskWrapper;

public class LocalProcess {
    protected static final Logger LOGGER = LoggerFactory.getLogger(LocalProcess.class);

    public static void main(String[] args)
            throws IllegalAccessException, InstantiationException, InvocationTargetException, NoSuchMethodException,
                   ClassNotFoundException {
        HashMap<String, String> parameters = new HashMap<String, String>() {{
            put("args", String.join(" ", args));
        }};

        LocalProcess.runTask(parameters);
    }

    public static void runTask(Map<String, String> runtimeParameters)
            throws IllegalAccessException, InstantiationException, InvocationTargetException, NoSuchMethodException,
                   ClassNotFoundException {
        String taskWrapperClassName = System.getenv("TASK_WRAPPER_CLASS");
        LOGGER.debug("Task Wrapper Class: " + taskWrapperClassName);
        if (taskWrapperClassName == null) {
            throw new IllegalArgumentException("TASK_WRAPPER_CLASS environment variable is not set.");
        }
        Class taskWrapperClass = PluginImporter.importPlugin(taskWrapperClassName);
        Constructor taskWrapperConstructor = taskWrapperClass.getConstructor(new Class[] {Map.class});

        TaskWrapper taskWrapper = (TaskWrapper) taskWrapperConstructor.newInstance(runtimeParameters);

        taskWrapper.run();
    }
}
