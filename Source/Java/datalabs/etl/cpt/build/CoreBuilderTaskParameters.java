package datalabs.etl.cpt.build;

import java.lang.reflect.InvocationTargetException;
import java.util.Map;

import datalabs.parameter.Parameters;


public class CoreBuilderTaskParameters extends Parameters {
    public String output_directory;
    public String prior_dtk_version;
    public String current_dtk_version;
    public String release_date;
    public Map<String, String> unknowns;

    public CoreBuilderTaskParameters(Map<String, String> parameters) throws IllegalAccessException, IllegalArgumentException {
        super(parameters);
    }
}
