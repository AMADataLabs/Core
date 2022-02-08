package datalabs.etl.dag.state.dynamodb;

import java.lang.reflect.InvocationTargetException;
import java.util.HashMap;
import java.util.Map;

import software.amazon.awssdk.services.dynamodb.DynamoDbClient;
import software.amazon.awssdk.services.dynamodb.model.AttributeValue;
import software.amazon.awssdk.services.dynamodb.model.DynamoDbException;
import software.amazon.awssdk.services.dynamodb.model.GetItemRequest;
import software.amazon.awssdk.services.dynamodb.model.PutItemRequest;
import software.amazon.awssdk.services.dynamodb.model.ResourceNotFoundException;

import datalabs.etl.dag.state.Status;
import datalabs.parameter.Parameters;


class DagStateParameters extends Parameters {
    String stateLockTable;
    String dagStateTable;
    Map<String, String> unknowns;

    DagStateParameters(Map<String, String> parameters) throws IllegalAccessException, IllegalArgumentException {
        super(parameters);
    }
}


public class DagState extends datalabs.etl.dag.state.DagState {
    public DagState(Map<String, String> parameters)
            throws IllegalAccessException, InstantiationException, InvocationTargetException, NoSuchMethodException {
        super(parameters);
    }

    public Status getDagStatus(String dag, String executionTime)
            throws IllegalArgumentException, DynamoDbException {
        return getTaskStatus(dag, "DAG", executionTime);
    }

    public Status getTaskStatus(String dag, String task, String executionTime)
            throws IllegalArgumentException, DynamoDbException {
        Map<String, AttributeValue> item = getItem(dag, task, executionTime);

        if (item == null) {
            throw new IllegalArgumentException("Unable to find status for \"" + dag + "\" DAG task \"" + task + "\"");
        }

        return Status.valueOf(item.get("status").toString());
    }

    public void setDagStatus(String dag, String executionTime, Status status)
            throws IllegalArgumentException, DynamoDbException {
        setTaskStatus(dag, "DAG", executionTime, status);
    }

    public void setTaskStatus(String dag, String task, String executionTime, Status status)
            throws IllegalArgumentException, DynamoDbException {
        putItem(dag, task, executionTime, status);
    }

    Map<String, AttributeValue> getItem(String dag, String task, String executionTime) throws DynamoDbException {
        DynamoDbClient dynamoDb = DynamoDbClient.builder().build();
        Map<String, AttributeValue> key = DagState.getKey(dag, task, executionTime);
        String table = ((DagStateParameters) this.parameters).dagStateTable;
        GetItemRequest request = GetItemRequest.builder().key(key).tableName(table).build();

        return dynamoDb.getItem(request).item();
    }

    void putItem(String dag, String task, String executionTime, Status status)
            throws ResourceNotFoundException, DynamoDbException {
        DynamoDbClient dynamoDb = DynamoDbClient.builder().build();
        String table = ((DagStateParameters) this.parameters).dagStateTable;
        HashMap<String,AttributeValue> columnValues = new HashMap<String,AttributeValue>() {{
            put("name", AttributeValue.builder().s(dag + "__" + task).build());
            put("executionTime", AttributeValue.builder().s(executionTime).build());
            put("status", AttributeValue.builder().s(status.getValue()).build());
        }};

        PutItemRequest request = PutItemRequest.builder().tableName(table).item(columnValues).build();

        dynamoDb.putItem(request);
     }

    static HashMap<String, AttributeValue> getKey(String dag, String task, String executionTime) {
        return new HashMap<String, AttributeValue>() {{
            put("name", AttributeValue.builder().s(dag + "__" + task).build());
            put("executionTime", AttributeValue.builder().s(executionTime).build());
        }};
    }
}
