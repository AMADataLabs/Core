package datalabs.task;

import com.amazonaws.services.lambda.runtime.Context;

import datalabs.plugin.PluginImporter;
import datalabs.task.TaskWrapper;

public final class LocalProcess {
     public static void main(String[] args) {
        String task_wrapper_class_name = System.getProperty("TASK_WRAPPER_CLASS");
        Class task_wrapper_class = PluginImporter.importPlugin(task_wrapper_class_name);
        Constructor task_wrapper_constructor = task_wrapper_class.getContstructor(new Class[] {String[].class});
        TaskWrapper task_wrapper = task_wrapper_constructor.newInstance(args);

        task_wrapper.run();
     }
 }
