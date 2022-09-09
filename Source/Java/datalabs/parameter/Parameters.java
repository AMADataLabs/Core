package datalabs.parameter;

import java.lang.reflect.Field;
import java.lang.reflect.InvocationTargetException;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;
import java.util.ArrayList;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;


public abstract class Parameters {
    protected static final Logger LOGGER = LoggerFactory.getLogger(Parameters.class);

    protected Parameters() {
    }

    public Parameters(Map<String, String> parameters) throws IllegalAccessException, IllegalArgumentException, NoSuchFieldException {
        Field[] fields = getClass().getFields();
        LOGGER.info("Parameter Class: " + getClass());
        Map<String, String> fieldNames = Parameters.getFieldNames(fields);
        Map<String, String> fieldDefaults = getFieldDefaults(fields);

        Map<String, String> standardizedParameters = Parameters.standardizeParameters(parameters);

        validate(standardizedParameters, fields, fieldNames, fieldDefaults);

        populate(standardizedParameters, fieldNames, fieldDefaults);
    }

    public static Parameters fromMap(Map<String, String> parameters, Class parameterClass)
            throws IllegalAccessException, IllegalArgumentException, InstantiationException,
            InvocationTargetException, NoSuchMethodException {
        if (parameters == null) {
            throw new IllegalArgumentException("Null parameters map.");
        }

        return (Parameters) parameterClass.getConstructor(new Class[] {Map.class}).newInstance(parameters);
    }

    static Map<String, String> standardizeParameters(Map<String, String> parameters) throws NoSuchFieldException {
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
        LOGGER.info("Unexpected Fields: " + Arrays.toString(unexpectedFields));
        LOGGER.info("Missing Fields: " + Arrays.toString(missingFields));
        LOGGER.info("Default Fields: " + Arrays.toString(fieldDefaults.keySet().toArray()));

        if (unexpectedFields.length > 0) {
            moveUnknowns(parameters, fieldNames, unexpectedFields);
        }

        if (missingFields.length > 0) {
            throw new IllegalArgumentException(
                "The following parameters are missing: " + Arrays.toString(missingFields)
            );
        }
    }

    void populate(Map<String, String> parameters, Map<String, String> fieldNames, Map<String, String> fieldDefaults) {
        fieldDefaults.forEach(
            (key, value) -> setField(fieldNames.get(key), value)
        );

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

    Map<String, String> getFieldDefaults(Field[] fields) throws IllegalAccessException, NoSuchFieldException {
        HashMap<String, String> fieldDefaults = new HashMap<String, String>();

        for (Field field : fields) {
            Field declaredField = this.getClass().getField(field.getName());
            Optional optionalAnnotation = declaredField.getAnnotation(Optional.class);

            if (optionalAnnotation != null) {
                fieldDefaults.put(Parameters.standardizeName(declaredField.getName()), optionalAnnotation.value());
            }
        }

        return fieldDefaults;
    }

    static String[] getUnexpectedFields(Map<String, String> parameters, Map<String, String> fieldNames) {
        ArrayList<String> unexpectedFields = new ArrayList<String>();

        for (String fieldName : parameters.keySet()) {
            if (!fieldNames.keySet().stream().anyMatch(n -> n.equals(fieldName))) {
                unexpectedFields.add(fieldName);
            }
        }

        return Arrays.stream(unexpectedFields.toArray()).toArray(String[]::new);
    }

    static String[] getMissingFields(Map<String, String> parameters, Map<String, String> fieldNames, Map<String, String> fieldDefaults) {
        ArrayList<String> missingFields = new ArrayList<String>();

        for (String fieldName : fieldNames.keySet()) {
            boolean isUnknowns = fieldName.equals("UNKNOWNS");
            boolean inParameters = parameters.keySet().stream().anyMatch(n -> n.equals(fieldName));
            boolean hasDefault = fieldDefaults.get(fieldName) != null;

            if (!isUnknowns && !inParameters & !hasDefault) {
                missingFields.add(fieldName);
            }
        }

        return Arrays.stream(missingFields.toArray()).toArray(String[]::new);
    }

    static String standardizeName(String name) {
        Matcher matcher = Pattern.compile("(?<before>[a-z])(?<after>[A-Z])").matcher(name);
        String standardizedName = "";
        int index = 0;

        while (matcher.find()) {
            standardizedName += name.substring(index, matcher.start());

            standardizedName += matcher.group("before") + "_" + matcher.group("after");

            index = matcher.end();
        }

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

        setField("unknowns", unknowns);
    }

    void setField(String field, Object value) {
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
            if (field.equals("UNKNOWNS")) {
                hasUnknowns = true;
            }
        }

        return hasUnknowns;
    }
}
