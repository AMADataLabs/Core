package datalabs.etl.cpt.build;

import java.lang.reflect.InvocationTargetException;
import java.util.Map;

import datalabs.parameter.Parameters;


public class LinkBuilderParameters extends Parameters {
    public String hcpsTerminationDate;
    public String linkDate;
    public String linkIncrementalDate;
    public String linkAnnualDate;
    public String revisionDate;


    public Map<String, String> unknowns;

    public LinkBuilderParameters(Map<String, String> parameters) throws IllegalAccessException, IllegalArgumentException, NoSuchFieldException {
        super(parameters);
    }
}
