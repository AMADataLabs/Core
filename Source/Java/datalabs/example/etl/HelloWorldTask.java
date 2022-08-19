package datalabs.example.etl;

import java.lang.reflect.InvocationTargetException;
import java.util.Map;
import java.util.ArrayList;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import datalabs.task.Task;


public class HelloWorldTask extends Task {
    static final Logger LOGGER = LoggerFactory.getLogger(HelloWorldTask.class);

    public HelloWorldTask(Map<String, String> parameters)
            throws IllegalAccessException, InstantiationException, InvocationTargetException, NoSuchMethodException {
        super(parameters);
    }

    public HelloWorldTask(Map<String, String> parameters, ArrayList<byte[]> data)
            throws IllegalAccessException, InstantiationException, InvocationTargetException, NoSuchMethodException {
        super(parameters, data);
    }

    public ArrayList<byte[]> run() {
        LOGGER.info("Hello, World!");

        return null;
    }
}
