package datalabs.etl.cpt.build;

import java.lang.reflect.InvocationTargetException;
import java.util.Map;

import datalabs.parameter.Parameters;


public class CoreBuilderParameters extends Parameters {

    public String executionTime;
    public String host;
    public String username;
    public String password;
    public String port;
    public Map<String, String> unknowns;

    public CoreBuilderParameters(Map<String, String> parameters) throws IllegalAccessException, IllegalArgumentException, NoSuchFieldException {
        super(parameters);
    }
}
