package datalabs.example.etl;

import java.lang.reflect.InvocationTargetException;
import java.util.Map;
import java.util.Vector;

import org.apache.logging.log4j.Logger;
import org.apache.logging.log4j.LogManager;

import datalabs.task.Task;


public class HelloWorldTask extends Task {
    private static Class PARAMETER_CLASS = null;
    static final Logger LOGGER = LogManager.getLogger();

    public HelloWorldTask(Map<String, String> parameters)
            throws IllegalAccessException, InstantiationException, InvocationTargetException, NoSuchMethodException {
        super(parameters);
    }

    public HelloWorldTask(Map<String, String> parameters, Vector<byte[]> data)
            throws IllegalAccessException, InstantiationException, InvocationTargetException, NoSuchMethodException {
        super(parameters, data);
    }

    public void run() {
        LOGGER.info("Hello, World!");
    }
}
