package datalabs.etl.dag.state.dynamodb;

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

import datalabs.etl.dag.notify.SnsDagNotifier;


@TestMethodOrder(OrderAnnotation.class)
class SnsDagNotifierTests {
    protected static final Logger LOGGER = LoggerFactory.getLogger(SnsDagNotifierTests.class);

    static final String DAG_TOPIC_ARN = "arn:aws:sns:us-east-1:644454719059:DataLake-sbx-DAGProcessor";

    @BeforeEach
    void beforeEach() {
    }

    @Test
    @DisplayName("notify() for BABYLON5 on 2256-03-09 08:00:00 succeeds")
    @EnabledIfSystemProperty(named="integration-tests", matches="true")
    @Order(1)
    void notifySucceeds() {
        try {
            SnsDagNotifier notifier = new SnsDagNotifier(SnsDagNotifierTests.DAG_TOPIC_ARN);

            notifier.notify("BABYLON5", "2256-03-09 08:00:00");
        } catch (
            Exception exception
        ) {
            exception.printStackTrace();
            Assertions.assertTrue(false);
        }
    }
}
