package datalabs.task;

import java.lang.reflect.Type;
import java.util.Map;

import com.google.gson.Gson;

import datalabs.task.Parameters;


public abstract class TaskWrapper {
    private static Class PARAMETER_CLASS = null;
    private Parameters parameters = null;
    private byte[] data = null;

    public TaskWrapper(String parameters) {
        this.parameters = new Gson().fromJson(parameters, PARAMETER_CLASS);
    }

    public TaskWrapper(String parameters, byte[] data) {
        TaskWrapper(parameters);

        this.data = data;
    }

    public abstract void run();
}
