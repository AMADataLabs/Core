package datalabs.etl.cpt.build;

import java.lang.reflect.InvocationTargetException;
import java.util.Map;

import datalabs.parameter.Parameters;


public class ConsumerClinicianDescriptorsBuilderParameters extends Parameters {
    public String versionNew;
    public Map<String, String> unknowns;

    public ConsumerClinicianDescriptorsBuilderParameters(Map<String, String> parameters) throws
            IllegalAccessException, IllegalArgumentException, NoSuchFieldException {
        super(parameters);
    }
}
