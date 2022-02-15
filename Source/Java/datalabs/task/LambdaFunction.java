package datalabs.task;

import java.lang.reflect.Constructor;
import java.lang.reflect.InvocationTargetException;
import java.util.Map;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.LambdaLogger;
import com.amazonaws.services.lambda.runtime.RequestHandler;

import datalabs.plugin.PluginImporter;
import datalabs.task.TaskWrapper;

public class LambdaFunction implements RequestHandler<Map<String,String>, String> {
    @Override
     public String handleRequest(Map<String,String> event, Context context) {
        String taskWrapperClassName = System.getProperty("TASK_WRAPPER_CLASS");
        TaskWrapper taskWrapper;
        String response;

        try {
            taskWrapper = this.createTaskWrapper(taskWrapperClassName, event);

            response = taskWrapper.run();
        } catch (Exception exception) {
            response = exception.getMessage();
        }

        return response;
     }

     TaskWrapper createTaskWrapper(String taskWrapperClassName, Map<String,String> event)
            throws IllegalAccessException, InstantiationException, InvocationTargetException, NoSuchMethodException,
                   ClassNotFoundException {
         Class taskWrapperClass = PluginImporter.importPlugin(taskWrapperClassName);
         Constructor taskWrapperConstructor = taskWrapperClass.getConstructor(new Class[] {Map.class});

         return (TaskWrapper) taskWrapperConstructor.newInstance(event);
     }
 }
