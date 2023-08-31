package datalabs.etl.dag.state.dynamodb;

import java.lang.reflect.InvocationTargetException;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import software.amazon.awssdk.services.dynamodb.DynamoDbClient;
import software.amazon.awssdk.services.dynamodb.model.AttributeValue;
import software.amazon.awssdk.services.dynamodb.model.ConditionalCheckFailedException;
import software.amazon.awssdk.services.dynamodb.model.DynamoDbException;
import software.amazon.awssdk.services.dynamodb.model.DeleteItemRequest;
import software.amazon.awssdk.services.dynamodb.model.GetItemRequest;
import software.amazon.awssdk.services.dynamodb.model.PutItemRequest;
import software.amazon.awssdk.services.dynamodb.model.ResourceNotFoundException;

import datalabs.etl.dag.state.Status;
import datalabs.parameter.Parameters;


public class DagState extends datalabs.etl.dag.state.DagState {
    protected static final Logger LOGGER = LoggerFactory.getLogger(DagState.class);

    static final int TIMEOUT_MILLISECONDS = 30000;

    public DagState(Map<String, String> parameters)
            throws IllegalAccessException, InstantiationException, InvocationTargetException, NoSuchMethodException {
        super(parameters, DagStateParameters.class);

        LOGGER.debug("State Lock Table: " + ((DagStateParameters) this.parameters).lockTable);
        LOGGER.debug("DAG State Table: " + ((DagStateParameters) this.parameters).stateTable);
    }

    public Status getDagStatus(String dag, String executionTime)
            throws IllegalArgumentException, DynamoDbException {
        return getTaskStatus(dag, null, executionTime);
    }

    public Status getTaskStatus(String dag, String task, String executionTime)
            throws IllegalArgumentException, DynamoDbException {
        Status status = Status.UNKNOWN;

        Map<String, AttributeValue> item = getItem(dag, task, executionTime);

        if (item == null) {
            throw new IllegalArgumentException("Unable to query DAG state table.");
        } else if (item.containsKey("status")) {
            LOGGER.debug("Get Item Response: " + item);
            LOGGER.debug("Status: " + item.get("status").s());

            status = Status.fromValue(item.get("status").s());
        }

        return status;
    }

    public void setDagStatus(String dag, String executionTime, Status status)
            throws IllegalArgumentException, DynamoDbException {
        setTaskStatus(dag, null, executionTime, status);
    }

    public void setTaskStatus(String dag, String task, String executionTime, Status status)
            throws IllegalArgumentException, DynamoDbException {
        putItem(dag, task, executionTime, status);
    }

    boolean lockState(String dag, String task, String executionTime) {
        DynamoDbClient dynamoDb = DynamoDbClient.builder().build();
        String table = ((DagStateParameters) this.parameters).lockTable;
        Map<String, AttributeValue> lockId = getLockId(dag, task, executionTime);
        long start_time = new Date().getTime();
        boolean locked = false;

        while (!locked && (new Date().getTime()-start_time) < DagState.TIMEOUT_MILLISECONDS) {
            long current_time = new Date().getTime();

            try {
                PutItemRequest request = PutItemRequest.builder().tableName(table).item(
                    new HashMap<String,AttributeValue>() {{
                        putAll(lockId);
                        put("ttl", AttributeValue.builder().n(String.valueOf((int) (current_time/1000)+30)).build());
                    }}
                ).conditionExpression(
                    "attribute_not_exists(#r)"
                ).expressionAttributeNames(
                    new HashMap<String, String>() {{
                        put("#r", "LockID");
                    }}
                ).build();

                dynamoDb.putItem(request);

                locked = true;
            } catch (ConditionalCheckFailedException exception) {
                // ignore
            }
        }

        return locked;
    }

    boolean unlockState(String dag, String task, String executionTime) {
        DynamoDbClient dynamoDb = DynamoDbClient.builder().build();
        String table = ((DagStateParameters) this.parameters).lockTable;
        Map<String, AttributeValue> lockId = getLockId(dag, task, executionTime);
        boolean unlocked = false;

        try {
            DeleteItemRequest request = DeleteItemRequest.builder().tableName(table).key(
                lockId
            ).conditionExpression(
                "attribute_exists(#r)"
            ).expressionAttributeNames(
                new HashMap<String, String>() {{
                    put("#r", "LockID");
                }}
            ).build();

            dynamoDb.deleteItem(request);

            unlocked = true;
        } catch (ConditionalCheckFailedException exception) {
            // ignore
        }

        return unlocked;
    }

    Map<String, AttributeValue> getItem(String dag, String task, String executionTime) throws DynamoDbException {
        DynamoDbClient dynamoDb = DynamoDbClient.builder().build();
        Map<String, AttributeValue> key = DagState.getKey(dag, task, executionTime);
        String table = ((DagStateParameters) this.parameters).stateTable;
        GetItemRequest request = GetItemRequest.builder().key(key).tableName(table).build();
        LOGGER.debug("Get Item Request: " + request);

        return dynamoDb.getItem(request).item();
    }

    void putItem(String dag, String task, String executionTime, Status status)
            throws ResourceNotFoundException, DynamoDbException {
        DynamoDbClient dynamoDb = DynamoDbClient.builder().build();
        Map<String, AttributeValue> key = DagState.getKey(dag, task, executionTime);
        String table = ((DagStateParameters) this.parameters).stateTable;
        HashMap<String,AttributeValue> columnValues = new HashMap<String,AttributeValue>() {{
            put("name", AttributeValue.builder().s(key.get("name").s()).build());
            put("execution_time", AttributeValue.builder().s(executionTime).build());
            put("status", AttributeValue.builder().s(status.getValue()).build());
        }};

        PutItemRequest request = PutItemRequest.builder().tableName(table).item(columnValues).build();
        LOGGER.debug("Put Item Request: " + request);

        final String response = dynamoDb.putItem(request).toString();
        LOGGER.debug("Put Item Response: " + response);
     }

    static HashMap<String, AttributeValue> getLockId(String dag, String task, String executionTime) {
        String lockId = dag;

        if (task != null) {
            lockId += "__" + task;
        }

        lockId += "__" + executionTime;

        final String finalLockId = lockId;
        return new HashMap<String, AttributeValue>() {{
            put("LockID", AttributeValue.builder().s(finalLockId).build());
        }};
    }

    static HashMap<String, AttributeValue> getKey(String dag, String task, String executionTime) {
        String name = dag;

        if (task != null) {
            name += "__" + task;
        }

        AttributeValue nameAttribute = AttributeValue.builder().s(name).build();

        return new HashMap<String, AttributeValue>() {{
            put("name", nameAttribute);
            put("execution_time", AttributeValue.builder().s(executionTime).build());
        }};
    }
}
