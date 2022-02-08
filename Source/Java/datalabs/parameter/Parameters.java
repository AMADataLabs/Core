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

import org.apache.logging.log4j.Logger;
import org.apache.logging.log4j.LogManager;


public abstract class Parameters {
    protected static final Logger LOGGER = LogManager.getLogger();

    public Parameters(Map<String, String> parameters) throws IllegalAccessException, IllegalArgumentException {
        Field[] fields = getClass().getFields();
        Map<String, String> fieldNames = Parameters.getFieldNames(fields);

        validate(parameters, fields, fieldNames);

        populate(parameters, fields, fieldNames);
    }

    void validate(Map<String, String> parameters, Field[] fields, Map<String, String> fieldNames)
            throws IllegalArgumentException {
        String[] unexpectedFields = Parameters.getUnexpectedFields(parameters, fieldNames);
        String[] missingFields = Parameters.getMissingFields(parameters, fieldNames);

        if (unexpectedFields.length > 0) {
            addUnknowns(parameters, fieldNames, unexpectedFields);
        }

        if (missingFields.length > 0) {
            throw new IllegalArgumentException(
                "The following parameters are missing: " + Arrays.toString(missingFields)
            );
        }
    }

    void populate(Map<String, String> parameters, Field[] fields, Map<String, String> fieldNames)
            throws IllegalAccessException {
        Arrays.stream(fields).forEach(
            field -> setField(field, parameters.get(fieldNames.get(field.getName())))
        );
    }

    static Map<String, String> getFieldNames(Field[] fields) {
        HashMap<String, String> fieldNames = new HashMap<String, String>();

        for (Field field : fields) {
            fieldNames.put(Parameters.canonicalizeName(field.getName()), field.getName());
        }

        return fieldNames;
    }

    static String[] getUnexpectedFields(Map<String, String> parameters, Map<String, String> fieldNames) {
        Vector<String> unexpectedFields = new Vector<String>();

        for (String fieldName : parameters.keySet()) {
            if (fieldNames.keySet().stream().anyMatch(n -> n.equals(fieldName))) {
                unexpectedFields.add(fieldName);
            }
        }

        return (String[]) unexpectedFields.toArray();
    }

    static String[] getMissingFields(Map<String, String> parameters, Map<String, String> fieldNames) {
        Vector<String> missingFields = new Vector<String>();

        for (String fieldName : fieldNames.keySet()) {
            if (!parameters.keySet().stream().anyMatch(n -> n.equals(fieldName))) {
                missingFields.add(fieldName);
            }
        }

        return (String[]) missingFields.toArray();
    }

    static String canonicalizeName(String name) {
        String lower_name = name.toLowerCase();
        Matcher matcher = Pattern.compile("_(?<letter>[a-z])}").matcher(lower_name);
        String canonicalizedName = "";
        int index = 0;

        while (matcher.find()) {
            canonicalizedName += lower_name.substring(index, matcher.start());

            canonicalizedName += matcher.group("letter").toUpperCase();

            index = matcher.end();
        }

        canonicalizedName += lower_name.substring(index);

        return canonicalizedName;
    }

    void addUnknowns(Map<String, String> parameters, Map<String, String> fieldNames, String[] unexpectedFields)
            throws IllegalArgumentException {
        HashMap<String, String> unknowns = new HashMap<String, String>();

        if (!hasUnknownsField(fieldNames.keySet())) {
            throw new IllegalArgumentException(
                "The following parameters are not expected: " + Arrays.toString(unexpectedFields)
            );
        }


        for (String field : unexpectedFields) {
            unknowns.put(field, parameters.get(field));
        }

        try {
            setField(getClass().getField("unknowns"), unknowns);
        } catch (NoSuchFieldException exception) {
            exception.printStackTrace();
            LOGGER.error(exception.getMessage());
        }
    }

    void setField(Field field, Object value) {
        try {
            field.set(this, value);
        } catch (IllegalAccessException exception) {
            LOGGER.error("Unable to set value for field " + field.getName());
            exception.printStackTrace();
        }
    }



    static boolean hasUnknownsField(Set<String> fieldNames) {
        boolean hasUnknowns = false;


        for (String field : fieldNames) {
            if (field == "unknowns") {
                hasUnknowns = true;
            }
        }

        return hasUnknowns;
    }
}
