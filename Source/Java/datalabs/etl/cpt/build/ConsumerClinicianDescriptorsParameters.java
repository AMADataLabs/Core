package datalabs.etl.cpt.build;

import java.lang.reflect.InvocationTargetException;
import java.util.Map;

import datalabs.parameter.Parameters;


public class ConsumerClinicianDescriptorsParameters extends Parameters {
    public String versionOld;
    public String versionNew;
    public Map<String, String> unknowns;

    public ConsumerClinicianDescriptorsParameters(Map<String, String> parameters) throws
            IllegalAccessException, IllegalArgumentException, NoSuchFieldException {
        super(parameters);
    }
}