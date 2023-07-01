package datalabs.etl.dag.aws;

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
import software.amazon.awssdk.services.dynamodb.model.DynamoDbException;

import datalabs.etl.dag.notify.sns.DagNotifier;


class AwsDagTaskWrapperTests {
    protected static final Logger LOGGER = LoggerFactory.getLogger(AwsDagTaskWrapperTests.class);

    @BeforeEach
    void beforeEach() {
    }

    @Test
    @DisplayName("Test Get DAG Name from DAG ID with Run Index")
    void dagIdWithRunIndexSplits() {
        String dagId = "HUBALOO:0";
        String[] dagIdParts = dagId.split(":");

        Assertions.assertEquals(dagIdParts.length, 2);
        Assertions.assertEquals(dagIdParts[0], "HUBALOO");
        Assertions.assertEquals(dagIdParts[1], "0");
    }

    @Test
    @DisplayName("Test Creating Task Wrapper Without Environment Variable")
    void createTaskWrapperSucceeds() {
        Map<String, String> environment = new HashMap<String, String>() {{
            put("DYNAMODB_CONFIG_TABLE", "DataLake-bogus-config");
        }};
        Map<String, String> parameters = new HashMap<String, String>() {{
            put("args", "createTaskWrapperSucceeds {}");
        }};

        AwsDagTaskWrapper taskWrapper = new AwsDagTaskWrapper(environment, parameters);
    }

    @Test
    @DisplayName("Test Getting DAG State Plugin")
    void getDagStatePluginSucceeds() {
        Map<String, String> environment = new HashMap<String, String>() {{
            put("DYNAMODB_CONFIG_TABLE", "DataLake-bogus-config");
        }};
        Map<String, String> parameters = new HashMap<String, String>() {{
            put("args", "createTaskWrapperSucceeds {}");
        }};
        AwsDagTaskWrapper taskWrapper = new AwsDagTaskWrapper(environment, parameters);

        taskWrapper.taskParameters = new HashMap<String, String>() {{
            put(
                "DAG_STATE",
                "{\"CLASS\":\"datalabs.etl.dag.state.dynamodb.DagState\",\"stateTable\":\"Fu\",\"lockTable\":\"Bar\"}"
            );
        }};

        try {
            taskWrapper.getDagStatePlugin();
            Assertions.assertTrue(true);
        } catch (Exception exception) {
            Assertions.assertTrue(false);
        }
    }

    @Test
    @DisplayName("Test Getting DynamoDB Parameters Using Run Index")
    @EnabledIfSystemProperty(named="integration-tests", matches="true")
    void getDynamoDbParametersUsingRunIndex() {
        Map<String, String> environment = new HashMap<String, String>() {{
            put("DYNAMODB_CONFIG_TABLE", "DataLake-configuration-sbx");
        }};
        AwsDagTaskWrapper taskWrapper = new AwsDagTaskWrapper(environment, new HashMap<String, String>());

        taskWrapper.getDagTaskParametersFromDynamoDb("HELLO_WORLD_JAVA:0", "DAG");
    }
}
