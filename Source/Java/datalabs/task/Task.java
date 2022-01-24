package datalabs.task;

import java.lang.reflect.InvocationTargetException;
import java.util.Map;
import java.util.Vector;

import datalabs.task.Parameters;


public abstract class Task {
    private static Class PARAMETER_CLASS = null;
    private Parameters parameters = null;
    private Vector<byte[]> data = null;

    public Task(Map<String, String> parameters)
            throws IllegalAccessException, InstantiationException, InvocationTargetException, NoSuchMethodException {
        this.parameters = (Parameters) PARAMETER_CLASS.getConstructor(new Class[] {Map.class}).newInstance(parameters);
    }

    public Task(Map<String, String> parameters, Vector<byte[]> data)
            throws IllegalAccessException, InstantiationException, InvocationTargetException, NoSuchMethodException {
        this(parameters);

        this.data = data;
    }

    public abstract void run();

    public Vector<byte[]> getData() {
        return this.data;
    }
}
