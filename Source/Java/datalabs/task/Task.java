package datalabs.task;

import java.lang.reflect.InvocationTargetException;
import java.util.Map;
import java.util.Vector;

import datalabs.ParameterizedClassMixin;
import datalabs.task.Parameters;


public abstract class Task extends ParameterizedClassMixin {
    protected Vector<byte[]> data = null;

    public Task(Map<String, String> parameters)
            throws IllegalAccessException, InstantiationException, InvocationTargetException, NoSuchMethodException {
        super(parameters);
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
