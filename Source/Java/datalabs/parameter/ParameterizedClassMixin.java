package datalabs.parameter;

import java.lang.reflect.InvocationTargetException;
import java.util.Map;

import org.apache.logging.log4j.Logger;
import org.apache.logging.log4j.LogManager;


public class ParameterizedClassMixin {
    protected static final Logger LOGGER = LogManager.getLogger();

    protected Parameters parameters = null;

    private ParameterizedClassMixin() {
    }

    protected ParameterizedClassMixin(Map<String, String> parameters, Class parameterClass)
            throws IllegalAccessException, IllegalArgumentException, InstantiationException, InvocationTargetException, NoSuchMethodException {
        if (parameterClass != null) {
            if (parameters == null) {
                throw new IllegalArgumentException("A parameter class, but not parameters input map, was specified.")
;            }

            this.parameters = (Parameters) parameterClass.getConstructor(new Class[] {Map.class}).newInstance(parameters);
        }
    }
}
