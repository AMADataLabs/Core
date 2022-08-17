package datalabs.parameter;

import java.lang.reflect.InvocationTargetException;
import java.util.HashMap;
import java.util.Map;
import java.util.ArrayList;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import datalabs.parameter.Parameters;
import datalabs.task.Task;


class ExampleTaskParameters extends Parameters {
    protected static final Logger LOGGER = LoggerFactory.getLogger(ExampleTaskParameters.class);

    public String fee;
    public String fye;

    @Optional("fum")
    public String fo;

    public ExampleTaskParameters(Map<String, String> parameters) throws IllegalAccessException, IllegalArgumentException, NoSuchFieldException {
        super(parameters);
    }
}


class ExampleTask extends Task {
    protected static final Logger LOGGER = LoggerFactory.getLogger(ExampleTask.class);

    public ExampleTask(Map<String, String> parameters)
            throws IllegalAccessException, InstantiationException, InvocationTargetException, NoSuchMethodException {
        super(parameters, ExampleTaskParameters.class);
    }

    public ExampleTaskParameters getParameters() {
        return (ExampleTaskParameters) this.parameters;
    }

    public ArrayList<byte[]> run() {
        LOGGER.info("This is an example task class with parameters.");

        return null;
    }
}


class ParametersTests {
    protected static final Logger LOGGER = LoggerFactory.getLogger(ParametersTests.class);

    static HashMap<String, String> PARAMETERS;

    @BeforeEach
    void beforeEach() {
        ParametersTests.PARAMETERS = new HashMap<String, String>() {{
            put("FEE", "tick");
            put("FYE", "tack");
            put("FO", "toe");
        }};
    }

    @Test
    void taskParametersArePopulatedFromInputMap() {
        ExampleTaskParameters parameters = null;

        try {
            ExampleTask task = new ExampleTask(ParametersTests.PARAMETERS);

            parameters = task.getParameters();
        } catch (
            IllegalAccessException | IllegalArgumentException | InstantiationException |
            InvocationTargetException | NoSuchMethodException exception
        ) {
            exception.printStackTrace();
            Assertions.assertTrue(false);
        }

        Assertions.assertNotNull(parameters);
        Assertions.assertEquals("tick", parameters.fee);
        Assertions.assertEquals("tack", parameters.fye);
        Assertions.assertEquals("toe", parameters.fo);
    }

    @Test
    void taskParametersArePopulatedFromDefaults() {
        ExampleTaskParameters parameters = null;

        String fo = ParametersTests.PARAMETERS.remove("FO");

        Assertions.assertNotNull(fo);

        try {
            ExampleTask task = new ExampleTask(ParametersTests.PARAMETERS);

            parameters = task.getParameters();
        } catch (
            IllegalAccessException | IllegalArgumentException | InstantiationException |
            InvocationTargetException | NoSuchMethodException exception
        ) {
            exception.printStackTrace();
            Assertions.assertTrue(false);
        }

        Assertions.assertNotNull(parameters);
        Assertions.assertEquals("tick", parameters.fee);
        Assertions.assertEquals("tack", parameters.fye);
        Assertions.assertEquals("fum", parameters.fo);
    }
}
