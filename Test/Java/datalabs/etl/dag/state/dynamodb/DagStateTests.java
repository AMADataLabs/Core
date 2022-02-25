package datalabs.etl.dag.state.dynamodb;

import java.lang.reflect.InvocationTargetException;
import java.util.HashMap;
import java.util.Map;

import org.apache.logging.log4j.Logger;
import org.apache.logging.log4j.LogManager;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.MethodOrderer.OrderAnnotation;
import org.junit.jupiter.api.Order;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestMethodOrder;
import org.junit.jupiter.api.condition.EnabledIfSystemProperty;
import software.amazon.awssdk.services.dynamodb.model.DynamoDbException;

import datalabs.etl.dag.state.Status;
import datalabs.etl.dag.state.dynamodb.DagState;


@TestMethodOrder(OrderAnnotation.class)
class DagStateTests {
    protected static final Logger LOGGER = LogManager.getLogger();

    static HashMap<String, String> PARAMETERS;

    @BeforeEach
    void beforeEach() {
        DagStateTests.PARAMETERS = new HashMap<String, String>() {{
            put("STATE_LOCK_TABLE", "DataLake-scheduler-locks-sbx");
            put("DAG_STATE_TABLE", "DataLake-dag-state-sbx");
        }};

        LOGGER.debug("PARAMETERS: " + DagStateTests.PARAMETERS);
    }

    @Test
    @DisplayName("setDagState() for BABYLON5 on 2256-03-09 08:00:00 sets to Pending")
    @EnabledIfSystemProperty(named="integration-tests", matches="true")
    @Order(1)
    void setDagStateSucceeds() {
        try {
            DagState state = new DagState(DagStateTests.PARAMETERS);
            state.setDagStatus("BABYLON5", "2256-03-09 08:00:00", Status.PENDING);
        } catch (
            IllegalAccessException |
            InstantiationException |
            InvocationTargetException |
            NoSuchMethodException |
            DynamoDbException |
            NullPointerException exception
        ) {
            exception.printStackTrace();
            Assertions.assertTrue(false);
        }
    }

    @Test
    @DisplayName("getDagState() for BABYLON5 on 2021-11-23 01:00:00 returns Pending")
    @EnabledIfSystemProperty(named="integration-tests", matches="true")
    @Order(2)
    void getDagStateReturnsFailed() {
        try {
            DagState state = new DagState(DagStateTests.PARAMETERS);
            Status status = state.getDagStatus("BABYLON5", "2256-03-09 08:00:00");

            Assertions.assertEquals(Status.PENDING, status);
        } catch (
            IllegalAccessException |
            InstantiationException |
            InvocationTargetException |
            NoSuchMethodException |
            DynamoDbException |
            NullPointerException exception
        ) {
            exception.printStackTrace();
            Assertions.assertTrue(false);
        }
    }

    @Test
    @DisplayName("getDagState() for absent BABYLON4 on 2021-11-23 01:00:00 returns Unknown")
    @EnabledIfSystemProperty(named="integration-tests", matches="true")
    void getMissingDagStateThrowsException() {
        try {
            DagState state = new DagState(DagStateTests.PARAMETERS);
            Status status = state.getDagStatus("BABYLON4", "2256-03-09 08:00:00");

            Assertions.assertEquals(Status.UNKNOWN, status);
        } catch (
            IllegalAccessException |
            InstantiationException |
            InvocationTargetException |
            NoSuchMethodException |
            DynamoDbException |
            NullPointerException exception
        ) {
            exception.printStackTrace();
            Assertions.assertTrue(false);
        }
    }
}
