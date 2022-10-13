package datalabs.example.etl;

import java.lang.reflect.InvocationTargetException;
import java.nio.charset.StandardCharsets;
import java.util.Map;
import java.util.ArrayList;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import datalabs.task.Task;


public class HelloWorldTask extends Task {
    static final Logger LOGGER = LoggerFactory.getLogger(HelloWorldTask.class);

    public HelloWorldTask(Map<String, String> parameters, ArrayList<byte[]> data)
            throws IllegalAccessException, InstantiationException, InvocationTargetException, NoSuchMethodException {
        super(parameters, null, HelloWorldParameters.class);
    }

    public ArrayList<byte[]> run() {
        HelloWorldParameters parameters = (HelloWorldParameters) this.parameters;
        String name = parameters.firstName;

        if (parameters.lastName != "") {
            name = name + " " + parameters.lastName;
        }

        String message = "Hello there, " + name + "!";
        LOGGER.info(message);

        return new ArrayList<byte[]>() {{
            add(message.getBytes(StandardCharsets.UTF_8));
        }};
    }
}
