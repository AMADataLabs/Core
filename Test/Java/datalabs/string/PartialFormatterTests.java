package datalabs.string;

import java.util.HashMap;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;


class PartialFormatterTests {
    protected static final Logger LOGGER = LoggerFactory.getLogger(PartialFormatterTests.class);

    static HashMap<String, Object> PARAMETERS;

    @BeforeEach
    void beforeEach() {
        PartialFormatterTests.PARAMETERS = new HashMap<String, Object>() {{
            put("tick", "Fee");
            put("tack", "Fye");
            put("toe", "Fo");
        }};
    }

    @Test
    void variablesAreReplacedWithValues() {
        String value = "The giant said, \"{tick}! {tack}! {toe}! {FUM}!\"";

        String resolvedValue = PartialFormatter.format(value, PartialFormatterTests.PARAMETERS);

        Assertions.assertEquals("The giant said, \"Fee! Fye! Fo! {FUM}!\"", resolvedValue);
    }

    @Test
    void allReferencesToSameVariableAreReplaced() {
        String value = "What is the {tick} for using your {tick}d {toe}rward network for {toe}ur hours?";

        String resolvedValue = PartialFormatter.format(value, PartialFormatterTests.PARAMETERS);

        Assertions.assertEquals("What is the Fee for using your Feed Forward network for Four hours?", resolvedValue);
    }
}
