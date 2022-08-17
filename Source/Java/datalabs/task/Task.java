package datalabs.task;

import java.lang.reflect.InvocationTargetException;
import java.util.Map;
import java.util.ArrayList;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import datalabs.parameter.ParameterizedClassMixin;
import datalabs.parameter.Parameters;


public abstract class Task extends ParameterizedClassMixin {
    protected static final Logger LOGGER = LoggerFactory.getLogger(Task.class);

    protected ArrayList<byte[]> inputData = null;
    protected ArrayList<byte[]> outputData = null;

    public Task(Map<String, String> parameters, ArrayList<byte[]> data)
            throws IllegalAccessException, InstantiationException, InvocationTargetException, NoSuchMethodException {
        this(parameters, data, null);
    }

    public Task(Map<String, String> parameters, ArrayList<byte[]> data, Class parameterClass)
            throws IllegalAccessException, InstantiationException, InvocationTargetException, NoSuchMethodException {
        this(parameters, parameterClass);

        this.inputData = data;
    }

    public Task(Map<String, String> parameters)
            throws IllegalAccessException, InstantiationException, InvocationTargetException, NoSuchMethodException {
        this(parameters, (Class) null);
    }

    public Task(Map<String, String> parameters, Class parameterClass)
            throws IllegalAccessException, InstantiationException, InvocationTargetException, NoSuchMethodException {
        super(parameters, parameterClass);
    }

    public abstract ArrayList<byte[]> run() throws TaskException;
}
