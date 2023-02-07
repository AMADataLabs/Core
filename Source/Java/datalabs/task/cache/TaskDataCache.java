package datalabs.task.cache;

import java.lang.reflect.InvocationTargetException;
import java.util.ArrayList;
import java.util.Map;

import datalabs.parameter.Parameters;


public abstract class TaskDataCache {
    public static enum Direction {
        INPUT, OUTPUT
    }

    protected Map<String, String> parameters = null;

    public TaskDataCache(Map<String, String> parameters)
            throws IllegalAccessException, InstantiationException, InvocationTargetException, NoSuchMethodException {
        this.parameters = parameters;
    }

    public abstract ArrayList<byte[]> extractData();

    public abstract void loadData(ArrayList<byte[]> outputData);
}
