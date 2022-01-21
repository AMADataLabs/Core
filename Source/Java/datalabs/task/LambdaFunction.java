package datalabs.task;

import java.lang.reflect.Constructor;
import java.util.Map;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.LambdaLogger;
import com.amazonaws.services.lambda.runtime.RequestHandler;

import datalabs.plugin.PluginImporter;
import datalabs.task.TaskWrapper;

public final class LambdaFunction implements RequestHandler<Map<String,String>, String> {
    @Override
     public String handleRequest(Map<String,String> event, Context context) {
        String taskWrapperClassName = System.getProperty("TASK_WRAPPER_CLASS");
        Class taskWrapperClass = PluginImporter.importPlugin(taskWrapperClassName);
        Constructor taskWrapperConstructor = taskWrapperClass.getContstructor(new Class[] {Map.class});
        TaskWrapper taskWrapper = taskWrapperConstructor.newInstance(new Object[event]);

        return taskWrapper.run();
     }
 }
