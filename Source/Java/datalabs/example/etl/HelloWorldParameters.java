package datalabs.example.etl;

import java.lang.reflect.InvocationTargetException;
import java.util.Map;

import datalabs.parameter.Parameters;
import datalabs.parameter.Optional;


public class HelloWorldParameters extends Parameters {
    public String firstName;

    @Optional
    public String lastName;
    @Optional
    public String executionTime;

    public Map<String, String> unknowns;

    public HelloWorldParameters(Map<String, String> parameters)
            throws IllegalAccessException, IllegalArgumentException, NoSuchFieldException {
        super(parameters);
    }
}
