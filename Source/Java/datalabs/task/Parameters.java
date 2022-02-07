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
        Field[] fields = getClass().getFields();

        Parameters.validate(parameters, fields);

        populate(parameters, fields);
    }

    static void validate(Map<String, String> parameters, Field[] fields) throws IllegalArgumentException {
        String[] fieldNames = Parameters.getFieldNames(fields);
        String[] unexpectedFields = Parameters.getUnexpectedFields(parameters, fieldNames);
        String[] missingFields = Parameters.getMissingFields(parameters, fieldNames);

        if (unexpectedFields.length > 0) {
            addUnknowns(parameters, fieldNames, unexpectedFields)
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

    static String[] getFieldNames(Map<String, String> fields) {
        Vector<String> fieldNames = new Vector<String>();

        for (Field field : fields) {
            fieldNames.add(field.getName());
        }

        return fieldNames.toArray();
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

    void addUnknowns(Map<String, String> parameters, String[] fieldNames, String[] unexpectedFields)
            throws IllegalArgumentException {
        HashMap<Sting, String> unknowns = new HashMap<String, String>();

        if (!hashUnknownsField(fieldNames)) {
            throw new IllegalArgumentException(
                "The following parameters are not expected: " + Arrays.toString(unexpectedFields)
            );
        }


        for (String field : unexpectedFields) {
            unknows.put(field, parameters.get(field));
        }

        setField(getClass().getField("unknowns"), unknowns);
    }

    void setField(Field field, String value) {
        try {
            field.set(this, value);
        } catch (IllegalAccessException exception) {
            LOGGER.error("Unable to set value for field " + field.getName());
            exception.printStackTrace();
        }
    }



    static boolean hashUnknownsField(String fieldNames) {
        boolean hasUnknowns = false;


        for (String field : fieldNames) {
            if (field == "unknowns") {
                hasUnknowns = true;
            }
        }

        return hasUnknowns;
    }
}
