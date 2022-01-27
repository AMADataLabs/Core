package datalabs.access.parameter;

import java.util.HashMap;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.apache.logging.log4j.Logger;
import org.apache.logging.log4j.LogManager;


public class ReferenceEnvironmentLoader {
    protected static final Logger LOGGER = LogManager.getLogger();

    Map<String, String> parameters;
    int matchLimit;

    private ReferenceEnvironmentLoader() {}

    public ReferenceEnvironmentLoader(Map<String, String> parameters) {
        this(parameters, 50);
    }

    public ReferenceEnvironmentLoader(Map<String, String> parameters, int matchLimit) {
        this.parameters = parameters;
        this.matchLimit = matchLimit;
    }

    public Map<String, String> load() {
        return load(null);
    }

    public Map<String, String> load(Map<String, String> environment) {
        if (environment == null) {
            environment = new HashMap(System.getenv());
        }

        Map<String, String> referenceVariables = getReferenceVariables(environment);

        Map<String, String> resolvedReferenceVariables = resolveReferenceVariables(referenceVariables, this.parameters);

        environment.putAll(resolvedReferenceVariables);

        return environment;
    }

    public static ReferenceEnvironmentLoader fromSystem() {
        return fromSystem(50);
    }

    public static ReferenceEnvironmentLoader fromSystem(int matchLimit) {
        Map<String, String> parameters = getReferentVariables(System.getenv());

        return new ReferenceEnvironmentLoader(parameters, matchLimit=matchLimit);
    }

    static Map<String, String> getReferenceVariables(Map<String, String> environment) {
        HashMap<String, String> referenceVariables = new HashMap<String, String>();

        environment.forEach(
            (key, value) -> addIfNotReferent(key, value, referenceVariables)
        );

        return referenceVariables;
    }

    static Map<String, String> resolveReferenceVariables(Map<String, String> variables, Map<String, String> parameters) {
        variables.forEach(
            (key, value) -> variables.put(key, resolveReferencesInValue(value, parameters))
        );

        return variables;
    }

    static Map<String, String> getReferentVariables(Map<String, String> environment) {
        HashMap<String, String> referentVariables = new HashMap<String, String>();

        environment.forEach(
            (key, value) -> addIfReferent(key, value, referentVariables)
        );

        return referentVariables;
    }

    static void addIfNotReferent(String key, String value, Map<String, String> referenceVariables) {
        if (Pattern.matches(".*\\$\\{[^${}]+\\}.*", value)) {
            referenceVariables.put(key, value);
        }
    }

    static void addIfReferent(String key, String value, Map<String, String> referentVariables) {
        if (!Pattern.matches(".*\\$\\{[^${}]+\\}.*", value)) {
            referentVariables.put(key, value);
        }
    }

    static String resolveReferencesInValue(String value, Map<String, String> parameters) {
        Matcher matcher = Pattern.compile("\\$\\{(?<name>[^${}]+)\\}").matcher(value);
        String resolvedValue = "";
        int index = 0;
        LOGGER.debug("Reference Value: " + value);

        while (matcher.find()) {
            resolvedValue += value.substring(index, matcher.start());

            resolvedValue += parameters.getOrDefault(matcher.group("name"), "${" + matcher.group("name") + "}");

            index = matcher.end();
            LOGGER.debug("Resolved Value (Part): " + resolvedValue);
        }

        resolvedValue += value.substring(index);
        LOGGER.debug("Resolved Value: " + resolvedValue);

        return resolvedValue;
    }
}
