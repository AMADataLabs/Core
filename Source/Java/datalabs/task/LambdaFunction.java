package datalabs.task;

import java.lang.reflect.Constructor;
import java.lang.reflect.InvocationTargetException;
import java.util.Map;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.LambdaLogger;
import com.amazonaws.services.lambda.runtime.RequestHandler;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import datalabs.access.parameter.ReferenceEnvironmentLoader;
import datalabs.plugin.PluginImporter;
import datalabs.task.TaskWrapper;

public class LambdaFunction implements RequestHandler<Map<String,String>, String> {
    static final Logger LOGGER = LoggerFactory.getLogger(LambdaFunction.class);

    @Override
     public String handleRequest(Map<String,String> event, Context context) {
        String taskWrapperClassName = System.getenv("TASK_WRAPPER_CLASS");
        TaskWrapper taskWrapper;
        String response;

        LOGGER.info("TaskWrapper: " + taskWrapperClassName);

        try {
            taskWrapper = this.createTaskWrapper(taskWrapperClassName, event);

            response = taskWrapper.run();
        } catch (Exception exception) {
            response = exception.getMessage();
        }

        LOGGER.info("TaskWrapper Response: " + response);

        return response;
     }

     TaskWrapper createTaskWrapper(String taskWrapperClassName, Map<String,String> event)
            throws IllegalAccessException, InstantiationException, InvocationTargetException, NoSuchMethodException,
                   ClassNotFoundException {
         ReferenceEnvironmentLoader environmentLoader = ReferenceEnvironmentLoader.fromSystem();
         Class taskWrapperClass = PluginImporter.importPlugin(taskWrapperClassName);
         Constructor taskWrapperConstructor = taskWrapperClass.getConstructor(new Class[] {Map.class, Map.class});

         return (TaskWrapper) taskWrapperConstructor.newInstance(environmentLoader.load(), event);
     }
}
