package datalabs.etl.dag;

import java.util.HashMap;
import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.MethodOrderer.OrderAnnotation;
import org.junit.jupiter.api.Order;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestMethodOrder;
import org.junit.jupiter.api.condition.EnabledIfSystemProperty;

import datalabs.etl.dag.cache.TaskDataCache;


class DagTaskWrapperTests {
    protected static final Logger LOGGER = LoggerFactory.getLogger(DagTaskWrapperTests.class);

    static HashMap<String, String> PARAMETER_MAP;

    @BeforeEach
    void beforeEach() {
        DagTaskWrapperTests.PARAMETER_MAP = new HashMap<String, String>() {{
            put("SOME_TASK_PARAMETER", "hoodoo");
            put("CACHE_INPUT_THIS_CACHE_PARAMETER", "voodoo");
            put("CACHE_OUTPUT_THAT_CACHE_PARAMETER", "voodoo");
            put("EXECUTION_TIME", "O dark thirty");
            put("CACHE_EXECUTION_TIME", "O dark thirty");
        }};
    }

    @Test
    @DisplayName("Test that extractCacheParameters separates cache parameters from task parameters")
    void extractCacheParametersDoes() {
        Map<TaskDataCache.Direction, Map<String, String>> cacheParameters
            = new HashMap<TaskDataCache.Direction, Map<String, String>>() {{
                put(TaskDataCache.Direction.INPUT, null);
                put(TaskDataCache.Direction.OUTPUT, null);
            }};

        Assertions.assertEquals(5, DagTaskWrapperTests.PARAMETER_MAP.size());
        DagTaskWrapper.extractCacheParameters(DagTaskWrapperTests.PARAMETER_MAP, cacheParameters);

        Assertions.assertEquals(2, DagTaskWrapperTests.PARAMETER_MAP.size());
        Assertions.assertTrue(DagTaskWrapperTests.PARAMETER_MAP.containsKey("SOME_TASK_PARAMETER"));
        Assertions.assertTrue(DagTaskWrapperTests.PARAMETER_MAP.containsKey("EXECUTION_TIME"));

        Map<String, String> inputCacheParameters = cacheParameters.get(TaskDataCache.Direction.INPUT);
        Assertions.assertEquals(2, inputCacheParameters.size());
        Assertions.assertTrue(inputCacheParameters.containsKey("THIS_CACHE_PARAMETER"));
        Assertions.assertTrue(inputCacheParameters.containsKey("EXECUTION_TIME"));

        Map<String, String> outputCacheParameters = cacheParameters.get(TaskDataCache.Direction.OUTPUT);
        Assertions.assertEquals(2, outputCacheParameters.size());
        Assertions.assertTrue(outputCacheParameters.containsKey("THAT_CACHE_PARAMETER"));
        Assertions.assertTrue(outputCacheParameters.containsKey("EXECUTION_TIME"));
    }
}
