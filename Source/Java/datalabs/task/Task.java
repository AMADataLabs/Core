package datalabs.task;

import java.lang.reflect.Type;
import java.util.HashMap;

import com.google.common.reflect.TypeToken;
import com.google.gson.Gson;

import datalabs.task.Parameters;


public abstract class Task {
    private static Class PARAMETER_CLASS = null;
    private Parameters parameters = null;

    public Task(String parameters, byte[] data=null) {
        this.parameters = new Gson().fromJson(parameters, PARAMETER_CLASS);
    }

    public abstract void run();
}
