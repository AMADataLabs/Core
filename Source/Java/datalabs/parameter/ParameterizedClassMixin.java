package datalabs.parameter;

import java.lang.reflect.InvocationTargetException;
import java.util.Map;


public class ParameterizedClassMixin {
    protected static Class PARAMETER_CLASS = null;
    protected Parameters parameters = null;

    public ParameterizedClassMixin(Map<String, String> parameters)
            throws IllegalAccessException, InstantiationException, InvocationTargetException, NoSuchMethodException {
        if (PARAMETER_CLASS != null) {
            this.parameters = (Parameters) PARAMETER_CLASS.getConstructor(new Class[] {Map.class}).newInstance(parameters);
        }
    }
}
