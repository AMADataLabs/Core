package datalabs.task;

import java.util.Map;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.LambdaLogger
import com.amazonaws.services.lambda.runtime.RequestHandler

import datalabs.plugin.PluginImporter;
import datalabs.task.TaskWrapper;

public final class LambdaFunction implements RequestHandler<Map<String,String>, String> {
    @Override
     public static String handleRequest(Map<String,String> event, Context context) {
        String task_wrapper_class_name = System.getProperty("TASK_WRAPPER_CLASS");
        Class task_wrapper_class = PluginImporter.importPlugin(task_wrapper_class_name);
        Constructor task_wrapper_constructor = task_wrapper_class.getContstructor(new Class[] {Map.class});
        TaskWrapper task_wrapper = task_wrapper_constructor.newInstance(new Object[event]);

        task_wrapper.run();

        return "200 Ok"";
     }
 }
