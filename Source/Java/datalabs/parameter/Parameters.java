package datalabs.parameter;

import java.lang.reflect.Field;
import java.lang.reflect.InvocationTargetException;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;
import java.util.Vector;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;


public abstract class Parameters {
    protected static final Logger LOGGER = LoggerFactory.getLogger(Parameters.class);

    public Parameters(Map<String, String> parameters) throws IllegalAccessException, IllegalArgumentException {
        Field[] fields = getClass().getFields();
        LOGGER.debug("Class: " + getClass());
        Map<String, String> fieldNames = Parameters.getFieldNames(fields);
        for (Field field : fields) {
            LOGGER.debug("Field: " + field.getName());
        }
        LOGGER.debug("Field Names: " + fieldNames);
        Map<String, String> fieldDefaults = getFieldDefaults(fields);

        parameters = Parameters.standardizeParameters(parameters);

        validate(parameters, fields, fieldNames, fieldDefaults);

        populate(parameters, fieldNames);
    }

    static Map<String, String> standardizeParameters(Map<String, String> parameters) {
        HashMap<String, String> standardizedParameters = new HashMap<String, String>();

        for (String key : parameters.keySet()) {
            standardizedParameters.put(Parameters.standardizeName(key), parameters.get(key));
        }

        return standardizedParameters;
    }

    void validate(Map<String, String> parameters, Field[] fields, Map<String, String> fieldNames, Map<String, String> fieldDefaults)
            throws IllegalArgumentException {
        String[] unexpectedFields = Parameters.getUnexpectedFields(parameters, fieldNames);
        String[] missingFields = Parameters.getMissingFields(parameters, fieldNames, fieldDefaults);
        LOGGER.debug("Parameters: " + parameters);
        LOGGER.debug("Unexpected Fields: " + Arrays.toString(unexpectedFields));
        LOGGER.debug("Missing Fields: " + Arrays.toString(missingFields));

        if (unexpectedFields.length > 0) {
            moveUnknowns(parameters, fieldNames, unexpectedFields);
        }

        if (missingFields.length > 0) {
            throw new IllegalArgumentException(
                "The following parameters are missing: " + Arrays.toString(missingFields)
            );
        }
    }

    void populate(Map<String, String> parameters, Map<String, String> fieldNames) {
        LOGGER.debug("Parameters: " + parameters);
        LOGGER.debug("Field Names: " + fieldNames);
        parameters.forEach(
            (key, value) -> setField(fieldNames.get(key), value)
        );
    }

    static Map<String, String> getFieldNames(Field[] fields) {
        HashMap<String, String> fieldNames = new HashMap<String, String>();

        for (Field field : fields) {
            fieldNames.put(Parameters.standardizeName(field.getName()), field.getName());
        }

        return fieldNames;
    }

    Map<String, String> getFieldDefaults(Field[] fields) throws IllegalAccessException {
        HashMap<String, String> fieldDefaults = new HashMap<String, String>();

        for (Field field : fields) {
            String value = (String) field.get(this);

            if (value != null) {
                fieldDefaults.put(Parameters.standardizeName(field.getName()), value);
            }
        }

        return fieldDefaults;
    }

    static String[] getUnexpectedFields(Map<String, String> parameters, Map<String, String> fieldNames) {
        Vector<String> unexpectedFields = new Vector<String>();

        for (String fieldName : parameters.keySet()) {
            LOGGER.debug("Validating field \"" + fieldName + "\"...");
            if (!fieldNames.keySet().stream().anyMatch(n -> n.equals(fieldName))) {
                unexpectedFields.add(fieldName);
            }
        }

        return Arrays.stream(unexpectedFields.toArray()).toArray(String[]::new);
    }

    static String[] getMissingFields(Map<String, String> parameters, Map<String, String> fieldNames, Map<String, String> fieldDefaults) {
        Vector<String> missingFields = new Vector<String>();

        for (String fieldName : fieldNames.keySet()) {
            boolean isUnknowns = fieldName.equals("UNKNOWNS");
            boolean isField = parameters.keySet().stream().anyMatch(n -> n.equals(fieldName));
            boolean hasDefault = fieldDefaults.get(fieldName) != null;

            if (!isUnknowns && !isField) {
                missingFields.add(fieldName);
            }
        }

        return Arrays.stream(missingFields.toArray()).toArray(String[]::new);
    }

    static String standardizeName(String name) {
        LOGGER.debug("Name: " + name);
        Matcher matcher = Pattern.compile("(?<before>[a-z])(?<after>[A-Z])").matcher(name);
        String standardizedName = "";
        int index = 0;

        while (matcher.find()) {
            standardizedName += name.substring(index, matcher.start());
            LOGGER.debug("Standardized Name: " + standardizedName);

            standardizedName += matcher.group("before") + "_" + matcher.group("after");
            LOGGER.debug("Standardized Name: " + standardizedName);

            index = matcher.end();
        }
        LOGGER.debug("Final Index: " + index);

        standardizedName += name.substring(index);

        return standardizedName.toUpperCase();
    }

    void moveUnknowns(Map<String, String> parameters, Map<String, String> fieldNames, String[] unexpectedFields)
            throws IllegalArgumentException {
        HashMap<String, String> unknowns = new HashMap<String, String>();

        if (!hasUnknownsField(fieldNames.keySet())) {
            throw new IllegalArgumentException(
                "The following parameters are not expected: " + Arrays.toString(unexpectedFields)
            );
        }

        for (String field : unexpectedFields) {
            unknowns.put(field, parameters.remove(field));
        }
        LOGGER.debug("Unknowns: " + unknowns);

        setField("unknowns", unknowns);
    }

    void setField(String field, Object value) {
        LOGGER.debug("Setting value of field " + field + " to " + value);
        try {
            getClass().getField(field).set(this, value);
        } catch (IllegalAccessException | NoSuchFieldException | NullPointerException exception) {
            LOGGER.error("Unable to set value for field " + field);
            exception.printStackTrace();
        }
    }



    static boolean hasUnknownsField(Set<String> fieldNames) {
        boolean hasUnknowns = false;

        for (String field : fieldNames) {
            LOGGER.debug("Field Name: |" + field + "|");
            if (field.equals("UNKNOWNS")) {
                LOGGER.debug("Flagging Has Unknowns...");
                hasUnknowns = true;
            }
        }
        LOGGER.debug("Has Unknowns: " + hasUnknowns);

        return hasUnknowns;
    }
}
