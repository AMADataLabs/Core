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
    public String emInputDirectory;
    public String emOutputDirectory;
    public String emDataFile;
    public String snomedInputDirectory;
    public String snomedOutputDirectory;
    public String snomedDataFile;
    public String headingsOutputDirectory;
    public String headingDataFile;
    public String rolesWorkBookOutputDirectory;
    public String exportDirectory;
    public String extractDirectory;
    public String version;
    public String incrementalVersion;
    public String annualVersion;
    public String linkDate;
    public String linkIncrementalDate;
    public String linkAnnualDate;
    public String revisionDate;
    public String priorHistoryDirectory;
    public String indexFile;
    public String guidelinesQAFile;
    public String editsFile;
    public String outputDirectory;
    public String indexFormat;


    public Map<String, String> unknowns;

    public DtkBuilderTaskParameters(Map<String, String> parameters) throws IllegalAccessException, IllegalArgumentException {
        super(parameters);
    }
}
