package datalabs.etl.cpt.build;

import java.lang.reflect.InvocationTargetException;
import java.util.Map;

import datalabs.parameter.Parameters;


public class CoreBuilderParameters extends Parameters {
    public String outputDirectory;
    public String priorLinkVersion;
    public String currentLinkVersion;
    public String releaseDate;
    public Map<String, String> unknowns;

    public CoreBuilderParameters(Map<String, String> parameters) throws IllegalAccessException, IllegalArgumentException, NoSuchFieldException {
        super(parameters);
    }
}
