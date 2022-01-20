package datalabs.task;

import com.amazonaws.services.lambda.runtime.Context;

import datalabs.plugin.PluginImporter

public final class Lambda {
     public static String handleRequest(String event, Context context) {
         task_wrapper_class_name = System.getProperty("TASK_WRAPPER_CLASS");
         task_wrapper_class = PluginImporter.importPlugin(task_wrapper_class_name);
         task_wrapper_constructor = task_wrapper_class.getContstructor([String]);
         task_wrapper = task_wrapper_constructor.newInstance([event]);

         task_wrapper.run();
     }
 }
