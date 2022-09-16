package datalabs.etl.cpt.build;

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

import org.ama.dtk.DtkAccess;
import datalabs.etl.dag.notify.sns.DagNotifier;


class CoreBuilderTaskTests {
    protected static final Logger LOGGER = LoggerFactory.getLogger(CoreBuilderTaskTests.class);

    @BeforeEach
    void beforeEach() {
    }

    @Test
    @DisplayName("Test DtkAccess.load() will throw an exception if the file arguments are invalid.")
    void dtkAccessLoadThrowsExceptionForInvalidFilePaths() {
        DtkAccess link = new DtkAccess();
        boolean success = false;

        try {
            link.load("bogus/path", "fake/path");
        } catch (java.lang.Exception exception) {
            CoreBuilderTaskTests.LOGGER.info("Expected exception: " + exception.toString());
            success = true;
        }

        Assertions.assertTrue(success);
    }
}
