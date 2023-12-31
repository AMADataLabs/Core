package datalabs.access.parameter;

import java.util.HashMap;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import datalabs.access.parameter.ReferenceEnvironmentLoader;


class ReferenceEnvironmentLoaderTests {
    protected static final Logger LOGGER = LoggerFactory.getLogger(ReferenceEnvironmentLoaderTests.class);

    static HashMap<String, String> ENVIRONMENT;

    @BeforeEach
    void beforeEach() {
        ReferenceEnvironmentLoaderTests.ENVIRONMENT = new HashMap<String, String>() {{
            put("REFERENT_VARIABLE", "Woopideedoo");
            put("SIMPLE_REFERENCE_VARIABLE", "${REFERENT_VARIABLE}");
            put("COMPLEX_REFERENCE_VARIABLE", "I said, \"${REFERENT_VARIABLE}!\"");
            put("PHRASE_VARIABLE", "I love you!");
            put("MULTI_REFERENCE_VARIABLE", "He said, \"${REFERENT_VARIABLE}, ${PHRASE_VARIABLE}\"");
            put("BAD_REFERENCE_VARIABLE", "${SOME_NONEXISTANT_VARIABLE}");
        }};
    }

    String getenv(String variable) {
        return (String) ReferenceEnvironmentLoaderTests.ENVIRONMENT.get(variable);
    }

    @Test
    @DisplayName("Matcher.find() Matches Partial String")
    void matcherFindMatchesPartialy() {
        String value = "He said, \"${REFERENT_VARIABLE}, ${PHRASE_VARIABLE}\"}";
        Matcher matcher = Pattern.compile("\\$\\{(?<name>[^${}]+)\\}").matcher(value);

        Assertions.assertTrue(matcher.find());
        Assertions.assertEquals("REFERENT_VARIABLE", matcher.group("name"));

        Assertions.assertTrue(matcher.find());
        Assertions.assertEquals("PHRASE_VARIABLE", matcher.group("name"));
    }

    @Test
    @DisplayName("Matcher.matches() Matches Full String")
    void matcherMatchesMatchesFully() {
        String value = "He said, \"${REFERENT_VARIABLE}, ${PHRASE_VARIABLE}\"}";
        Assertions.assertTrue(Pattern.matches(".*\\$\\{[^${}]+\\}.*", value));
    }

    @Test
    void getReferentVeriablesReturnsOnlyReferencelessVariables() {

        HashMap<String, String> parameters = ReferenceEnvironmentLoaderTests.ENVIRONMENT;
        ReferenceEnvironmentLoader loader = new ReferenceEnvironmentLoader(parameters);

        Map<String, String> referentVariables = ReferenceEnvironmentLoader.getReferentVariables(
            ReferenceEnvironmentLoaderTests.ENVIRONMENT
        );

        Assertions.assertEquals(2, referentVariables.size());
        Assertions.assertTrue(referentVariables.containsKey("REFERENT_VARIABLE"));
        Assertions.assertTrue(referentVariables.containsKey("PHRASE_VARIABLE"));
    }

    @Test
    void getReferenceVariablesReturnsNoReferencelessVariables() {
        HashMap<String, String> parameters = ReferenceEnvironmentLoaderTests.ENVIRONMENT;
        ReferenceEnvironmentLoader loader = new ReferenceEnvironmentLoader(parameters);

        Map<String, String> referenceVariables = ReferenceEnvironmentLoader.getReferenceVariables(
            ReferenceEnvironmentLoaderTests.ENVIRONMENT
        );

        Assertions.assertEquals(4, referenceVariables.size());
        Assertions.assertTrue(referenceVariables.containsKey("SIMPLE_REFERENCE_VARIABLE"));
        Assertions.assertTrue(referenceVariables.containsKey("COMPLEX_REFERENCE_VARIABLE"));
        Assertions.assertTrue(referenceVariables.containsKey("MULTI_REFERENCE_VARIABLE"));
        Assertions.assertTrue(referenceVariables.containsKey("BAD_REFERENCE_VARIABLE"));
    }

    @Test
    @DisplayName("resolveReferencesInValue() Matches Simple Reference")
    void resolveReferencesInValueMatchesSimpleReference() {
        HashMap<String, String> parameters = ReferenceEnvironmentLoaderTests.ENVIRONMENT;
        ReferenceEnvironmentLoader loader = new ReferenceEnvironmentLoader(parameters);
        Map<String, String> referentVariables = ReferenceEnvironmentLoader.getReferentVariables(
            ReferenceEnvironmentLoaderTests.ENVIRONMENT
        );
        String referenceValue = getenv("SIMPLE_REFERENCE_VARIABLE");
        String referentValue = getenv("REFERENT_VARIABLE");

        String resolvedValue = loader.resolveReferencesInValue(
            referenceValue,
            ReferenceEnvironmentLoaderTests.ENVIRONMENT,
            2
        );

        Assertions.assertEquals(referentValue, resolvedValue);
    }

    @Test
    @DisplayName("resolveReferencesInValue() Matches Complex Reference")
    void resolveReferencesInValueMatchesComplexReference() {
        HashMap<String, String> parameters = ReferenceEnvironmentLoaderTests.ENVIRONMENT;
        ReferenceEnvironmentLoader loader = new ReferenceEnvironmentLoader(parameters);
        Map<String, String> referentVariables = ReferenceEnvironmentLoader.getReferentVariables(
            ReferenceEnvironmentLoaderTests.ENVIRONMENT
        );
        String referenceValue = getenv("COMPLEX_REFERENCE_VARIABLE");
        String referentValue = "I said, \"Woopideedoo!\"";

        String resolvedValue = loader.resolveReferencesInValue(
            referenceValue,
            ReferenceEnvironmentLoaderTests.ENVIRONMENT,
            2
        );

        Assertions.assertEquals(referentValue, resolvedValue);
    }

    @Test
    @DisplayName("resolveReferencesInValue() Matches Multiple References")
    void resolveReferencesInValueMatchesMultipleReferences() {
        HashMap<String, String> parameters = ReferenceEnvironmentLoaderTests.ENVIRONMENT;
        ReferenceEnvironmentLoader loader = new ReferenceEnvironmentLoader(parameters);
        Map<String, String> referentVariables = ReferenceEnvironmentLoader.getReferentVariables(
            ReferenceEnvironmentLoaderTests.ENVIRONMENT
        );
        String referenceValue = getenv("MULTI_REFERENCE_VARIABLE");
        String referentValue = "He said, \"Woopideedoo, I love you!\"";

        String resolvedValue = loader.resolveReferencesInValue(
            referenceValue,
            ReferenceEnvironmentLoaderTests.ENVIRONMENT,
            2
        );

        Assertions.assertEquals(referentValue, resolvedValue);
    }

    @Test
    @DisplayName("resolveReferencesInValue() Matches Nested References")
    void resolveReferencesInValueMatchesNestedReferences() {
        HashMap<String, String> parameters = ReferenceEnvironmentLoaderTests.ENVIRONMENT;
        ReferenceEnvironmentLoader loader = new ReferenceEnvironmentLoader(parameters);
        Map<String, String> referentVariables = ReferenceEnvironmentLoader.getReferentVariables(
            ReferenceEnvironmentLoaderTests.ENVIRONMENT
        );
        String referenceValue = "I can too, ${SIMPLE_REFERENCE_VARIABLE}.";
        String referentValue = "I can too, Woopideedoo.";

        String resolvedValue = loader.resolveReferencesInValue(
            referenceValue,
            ReferenceEnvironmentLoaderTests.ENVIRONMENT,
            2
        );

        Assertions.assertEquals(referentValue, resolvedValue);
    }

    @Test
    @DisplayName("load() Matches All References")
    void loadResolvesAllReferences() {
        HashMap<String, String> parameters = ReferenceEnvironmentLoaderTests.ENVIRONMENT;
        ReferenceEnvironmentLoader loader = new ReferenceEnvironmentLoader(parameters);

        loader.load(ReferenceEnvironmentLoaderTests.ENVIRONMENT);

        Assertions.assertEquals(6, ReferenceEnvironmentLoaderTests.ENVIRONMENT.size());
        Assertions.assertEquals("Woopideedoo", getenv("REFERENT_VARIABLE"));
        Assertions.assertEquals("I love you!", getenv("PHRASE_VARIABLE"));
        Assertions.assertEquals("Woopideedoo", getenv("SIMPLE_REFERENCE_VARIABLE"));
        Assertions.assertEquals("I said, \"Woopideedoo!\"", getenv("COMPLEX_REFERENCE_VARIABLE"));
        Assertions.assertEquals("He said, \"Woopideedoo, I love you!\"", getenv("MULTI_REFERENCE_VARIABLE"));
        Assertions.assertEquals("${SOME_NONEXISTANT_VARIABLE}", getenv("BAD_REFERENCE_VARIABLE"));
    }
}
