package datalabs.access.parameter;

import java.util.Arrays;
import java.util.List;
import java.util.HashMap;
import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import datalabs.access.environment.VariableTree;


class VariableTreeTests {
    protected static final Logger LOGGER = LoggerFactory.getLogger(VariableTreeTests.class);

    static VariableTree TREE;

    @BeforeEach
    void beforeEach() {
        VariableTreeTests.TREE = VariableTree.generate(
            new HashMap<String, String>() {{
                put("ONE_TWO_BUCKLE", "foo");
                put("ONE_TWO_MY", "bar");
                put("ONE_TWO_SHOE", "party");
            }},
            "_"
        );
    }

    @Test
    @DisplayName("VariableTree.getValue() Returns Correct Branch Value")
    void getValueReturnsCorrectBranchValue() {
        assertEquals("foo", VariableTreeTests.TREE.getValue(new String[] {"ONE", "TWO", "BUCKLE"}));
        assertEquals("bar", VariableTreeTests.TREE.getValue(new String[] {"ONE", "TWO", "MY"}));
        assertEquals("party", VariableTreeTests.TREE.getValue(new String[] {"ONE", "TWO", "SHOE"}));
    }

    @Test
    @DisplayName("VariableTree.getBranches() Returns Correct Branch Names")
    void getBranchesReturnsCorrectBranchNames() {
        List branches = Arrays.asList(VariableTreeTests.TREE.getBranches(new String[] {"ONE", "TWO"}));

        for (String branch : new String[] {"BUCKLE", "MY", "SHOE"}) {
            assertTrue(branches.contains(branch));
        }
    }

    @Test
    @DisplayName("VariableTree.getBranchValue() Returns Correct Branch Values")
    void getBranchValuesReturnsCorrectBranchValues() {
        Map<String, String> values = VariableTreeTests.TREE.getBranchValues(new String[] {"ONE", "TWO"});
        HashMap<String, String> expectedValues = new HashMap<String, String>() {{
            put("BUCKLE", "foo");
            put("MY", "bar");
            put("SHOE", "party");
        }};

        expectedValues.forEach(
            (key, value) -> assertEquals(value, values.get(key))
        );
    }

    @Test
    @DisplayName("getValue() for Non-existant Branch Path Raises Exception")
    void getValueForBadPathRaisesException() {
        boolean caughtException = false;
        try {
            VariableTreeTests.TREE.getValue(new String[] {"ONE", "THREE"});
        } catch (IllegalArgumentException exception) {
            caughtException = true;
        }

        assertTrue(caughtException);
    }

    @Test
    @DisplayName("getBranches() for Non-existant Branch Path Raises Exception")
    void getBranchesForBadPathRaisesRaisesException() {
        boolean caughtException = false;
        try {
            VariableTreeTests.TREE.getBranches(new String[] {"ONE", "THREE"});
        } catch (IllegalArgumentException exception) {
            caughtException = true;
        }

        assertTrue(caughtException);
    }

    @Test
    @DisplayName("getBranchValues() for Non-existant Branch Path Raises Exception")
    void getValuesForBadPathRaisesRaisesException() {
        boolean caughtException = false;
        try {
            VariableTreeTests.TREE.getBranchValues(new String[] {"ONE", "THREE"});
        } catch (IllegalArgumentException exception) {
            caughtException = true;
        }

        assertTrue(caughtException);
    }
}
