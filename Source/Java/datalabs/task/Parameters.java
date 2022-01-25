package datalabs.task;

import java.lang.reflect.Field;
import java.util.Arrays;
import java.util.Map;
import java.util.Vector;

import org.apache.logging.log4j.Logger;
import org.apache.logging.log4j.LogManager;


public abstract class Parameters {
    protected static final Logger LOGGER = LogManager.getLogger();

    public Parameters(Map<String, String> parameters) throws IllegalAccessException, IllegalArgumentException {
        Field[] fields = this.getClass().getFields();

        Parameters.validate(parameters, fields);

        populate(parameters, fields);
    }

    static void validate(Map<String, String> parameters, Field[] fields) throws IllegalArgumentException {
        String[] fieldNames = new String[fields.length];
        String[] unexpectedFields = Parameters.getUnexpectedFields(parameters, fieldNames);
        String[] missingFields = Parameters.getMissingFields(parameters, fieldNames);

        if (unexpectedFields.length > 0) {
            throw new IllegalArgumentException(
                "The following parameters are not expected: " + Arrays.toString(unexpectedFields)
            );
        }

        if (missingFields.length > 0) {
            throw new IllegalArgumentException(
                "The following parameters are missing: " + Arrays.toString(missingFields)
            );
        }
    }

    void populate(Map<String, String> parameters, Field[] fields) throws IllegalAccessException {
        Arrays.stream(fields).forEach(
            field -> setField(field, parameters.get(field.getName()))
        );
    }

    static String[] getUnexpectedFields(Map<String, String> parameters, String[] fieldNames) {
        Vector<String> unexpectedFields = new Vector<String>();

        for (String fieldName : parameters.keySet()) {
            if (Arrays.stream(fieldNames).anyMatch(n -> n.equals(fieldName))) {
                unexpectedFields.add(fieldName);
            }
        }

        return (String[]) unexpectedFields.toArray();
    }

    static String[] getMissingFields(Map<String, String> parameters, String[] fieldNames) {
        Vector<String> missingFields = new Vector<String>();

        for (String fieldName : parameters.keySet()) {
            if (!parameters.keySet().stream().anyMatch(n -> n.equals(fieldName))) {
                missingFields.add(fieldName);
            }
        }

        return (String[]) missingFields.toArray();
    }

    void setField(Field field, String value) {
        try {
            field.set(this, value);
        } catch (IllegalAccessException exception) {
            LOGGER.error("Unable to set value for field " + field.getName());
            exception.printStackTrace();
        }
    }
}
