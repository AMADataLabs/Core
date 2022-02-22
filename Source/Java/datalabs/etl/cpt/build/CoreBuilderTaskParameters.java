package datalabs.etl.cpt.build;

import java.lang.reflect.InvocationTargetException;
import java.util.Map;

import datalabs.parameter.Parameters;


public class CoreBuilderTaskParameters extends Parameters {
    public String outputDirectory;
    public String priorDtkVersion;
    public String currentDtkVersion;
    public String releaseDate;
    public Map<String, String> unknowns;

    public CoreBuilderTaskParameters(Map<String, String> parameters) throws IllegalAccessException, IllegalArgumentException {
        super(parameters);
    }
}
