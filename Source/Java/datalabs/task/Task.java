package datalabs.task;

import java.lang.reflect.InvocationTargetException;
import java.util.Map;
import java.util.ArrayList;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import datalabs.parameter.Parameters;


public abstract class Task {
    protected static final Logger LOGGER = LoggerFactory.getLogger(Task.class);

    protected Parameters parameters = null;
    protected ArrayList<byte[]> data = null;

    public Task(Map<String, String> parameters, ArrayList<byte[]> data, Class parameterClass)
            throws IllegalAccessException, InstantiationException, InvocationTargetException, NoSuchMethodException {
        this.parameters = Parameters.fromMap(parameters, parameterClass);

        this.data = data;
    }

    public abstract ArrayList<byte[]> run() throws TaskException;
}
