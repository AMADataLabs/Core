package datalabs.task;

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

import datalabs.task.TaskWrapper;
import datalabs.task.cache.TaskDataCache;


class TaskWrapperTests {
    protected static final Logger LOGGER = LoggerFactory.getLogger(TaskWrapperTests.class);

    static HashMap<String, String> PARAMETER_MAP;

    @BeforeEach
    void beforeEach() {
        TaskWrapperTests.PARAMETER_MAP = new HashMap<String, String>() {{
            put("SOME_TASK_PARAMETER", "hoodoo");
            put("CACHE_INPUT_THIS_CACHE_PARAMETER", "voodoo");
            put("CACHE_OUTPUT_THAT_CACHE_PARAMETER", "voodoo");
            put("EXECUTION_TIME", "O dark thirty");
            put("CACHE_EXECUTION_TIME", "O dark thirty");
        }};
    }

    @Test
    @DisplayName("Test that extractCacheParameters extracts cache parameters from task parameters")
    void extractCacheParametersDoes() {
        Assertions.assertEquals(5, TaskWrapperTests.PARAMETER_MAP.size());
        Map<TaskDataCache.Direction, Map<String, String>> cacheParameters
            = new TaskWrapper(null, null).extractCacheParameters(TaskWrapperTests.PARAMETER_MAP);

        Assertions.assertEquals(5, TaskWrapperTests.PARAMETER_MAP.size());

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
