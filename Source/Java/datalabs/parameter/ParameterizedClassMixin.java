package datalabs.parameter;

import java.lang.reflect.InvocationTargetException;
import java.util.Map;

import org.apache.logging.log4j.Logger;
import org.apache.logging.log4j.LogManager;


public class ParameterizedClassMixin {
    protected static final Logger LOGGER = LogManager.getLogger();

    protected Parameters parameters = null;

    public ParameterizedClassMixin(Map<String, String> parameters)
            throws IllegalAccessException, InstantiationException, InvocationTargetException, NoSuchMethodException {
        this(parameters, null);
    }

    protected ParameterizedClassMixin(Map<String, String> parameters, Class parameterClass)
            throws IllegalAccessException, InstantiationException, InvocationTargetException, NoSuchMethodException {
        if (parameterClass != null) {
            this.parameters = (Parameters) parameterClass.getConstructor(new Class[] {Map.class}).newInstance(parameters);
        }
    }
}
