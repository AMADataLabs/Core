package datalabs.string;

import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class PartialFormatter {
    public static String format(String value, Map<String, Object> parameters) {
        String resolvedValue = value;

        for (Map.Entry<String, Object> entry : parameters.entrySet()) {
            String key = entry.getKey();

            resolvedValue = resolvedValue.replaceAll("\\{" + entry.getKey() + "\\}", entry.getValue().toString());
        }

        return resolvedValue;
    }
}
