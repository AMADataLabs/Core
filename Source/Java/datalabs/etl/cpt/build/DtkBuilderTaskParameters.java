package datalabs.etl.cpt.build;

import java.lang.reflect.InvocationTargetException;
import java.util.Map;

import datalabs.parameter.Parameters;


public class DtkBuilderTaskParameters extends Parameters {
    public String snomedDerbyHome;
    public String priorDtkVersion;
    public String releaseYear;
    public String releaseDate;
    public String priorYearlyRelease;
    public String hcpcsInputDirectory;
    public String hcpcsDataFile;

    public Map<String, String> unknowns;

    public DtkBuilderTaskParameters(Map<String, String> parameters) throws IllegalAccessException, IllegalArgumentException {
        super(parameters);
    }
}
