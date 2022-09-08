package datalabs.access.parameter;

import java.util.HashMap;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;


public class ReferenceEnvironmentLoader {
    protected static final Logger LOGGER = LoggerFactory.getLogger(ReferenceEnvironmentLoader.class);

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
        return load(new HashMap(System.getenv()));
    }

    public Map<String, String> load(Map<String, String> environment) {
        Map<String, String> referenceVariables = getReferenceVariables(environment);

        Map<String, String> resolvedReferenceVariables
            = resolveReferenceVariables(referenceVariables, this.parameters, this.matchLimit);

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

    static Map<String, String> resolveReferenceVariables(
        Map<String, String> variables,
        Map<String, String> parameters,
        int matchLimit
    ) {
        variables.forEach(
            (key, value) -> variables.put(key, resolveReferencesInValue(value, parameters, matchLimit))
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

    static String resolveReferencesInValue(String value, Map<String, String> parameters, int matchLimit) {
        Pattern pattern = Pattern.compile("\\$\\{(?<name>[^${}]+)\\}");
        Matcher matcher = pattern.matcher(value);
        int matchCount = 0;
        int index = 0;

        while (matcher.find(index) && matchCount < matchLimit) {
            LOGGER.debug("Value: " + value);
            LOGGER.debug("Match Start Index: " + index);
            String referenceName = matcher.group("name");
            String reference = "${" + referenceName + "}";
            String resolvedReference = parameters.getOrDefault(referenceName, reference);

            if (resolvedReference.equals(reference)) {
                index = matcher.end();
            } else {
                matchCount += 1;

                value = value.substring(0, matcher.start()) + resolvedReference + value.substring(matcher.end());
            }
            LOGGER.debug("Match Count: " + matchCount);

            matcher = pattern.matcher(value);
        }


        LOGGER.debug("Final Value: " + value);
        return value;
    }
}
