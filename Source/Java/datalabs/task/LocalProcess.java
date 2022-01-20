package datalabs.task;

import com.amazonaws.services.lambda.runtime.Context;

import datalabs.plugin.PluginImporter

public final class LocalProcess {
     public static void main(String[] args) {
         task_wrapper_class_name = System.getProperty("TASK_WRAPPER_CLASS");
         task_wrapper_class = PluginImporter.importPlugin(task_wrapper_class_name);
         task_wrapper_constructor = task_wrapper_class.getContstructor([String]);
         task_wrapper = task_wrapper_constructor.newInstance(args);

         task_wrapper.run();
     }
 }
