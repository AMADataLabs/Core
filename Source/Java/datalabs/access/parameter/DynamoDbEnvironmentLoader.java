package datalabs.access.parameter;

import java.util.HashMap;
import java.util.Map;

import com.google.gson.Gson;
import org.apache.logging.log4j.Logger;
import org.apache.logging.log4j.LogManager;
import software.amazon.awssdk.services.dynamodb.DynamoDbClient;
import software.amazon.awssdk.services.dynamodb.model.AttributeValue;
import software.amazon.awssdk.services.dynamodb.model.DynamoDbException;
import software.amazon.awssdk.services.dynamodb.model.GetItemRequest;

import datalabs.access.parameter.ReferenceEnvironmentLoader;


public class DynamoDbEnvironmentLoader {
    protected static final Logger LOGGER = LogManager.getLogger();

    String table;
    String dag;
    String task;

    private DynamoDbEnvironmentLoader() { }

    public DynamoDbEnvironmentLoader(String table, String dag, String task) {
        this.table = table;
        this.dag = dag;
        this.task = task;
    }

    public static DynamoDbEnvironmentLoader fromEnvironment() {
        return new DynamoDbEnvironmentLoader(
            System.getProperty("DYNAMODB_CONFIG_TABLE"),
            System.getProperty("DYNAMODB_CONFIG_DAG"),
            System.getProperty("DYNAMODB_CONFIG_TASK")
        );
    }

    public void load() {
        load(new HashMap(System.getenv()));
    }

    public Map<String, String> load(Map<String, String> environment) throws IllegalArgumentException {
        Map<String, String> globalVariables = getParametersFromDynamoDb("GLOBAL");
        Map<String, String> parameters = null;

        try {
            parameters = getParametersFromDynamoDb(this.task);
        } catch (DynamoDbException e) {
            System.err.println(e.getMessage());
            System.exit(1);
        }

        if (parameters == null) {
            throw new IllegalArgumentException(
                "No data in DynamoDB table \"" + this.table + "\" for " + this.dag + " DAG task \"" + this.task + "\"."
            );
        }

        parameters = (new ReferenceEnvironmentLoader(globalVariables)).load(parameters);

        environment.putAll(parameters);

        return environment;
    }

    Map<String, String> getParametersFromDynamoDb(String task) throws DynamoDbException {
        Map<String, AttributeValue> key = DynamoDbEnvironmentLoader.getKey(this.dag, task);
        LOGGER.debug("DynamoDB item key: " + key);

        return DynamoDbEnvironmentLoader.getParametersFromTable(this.table, key);
    }

    static HashMap<String, AttributeValue> getKey(String dag, String task) {
        return new HashMap<String, AttributeValue>() {{
            put("DAG", AttributeValue.builder().s(dag).build());
            put("Task", AttributeValue.builder().s(task).build());
        }};
    }

    static Map<String, String> getParametersFromTable(String table, Map<String, AttributeValue> key)
            throws DynamoDbException {
        DynamoDbClient dynamoDb = DynamoDbClient.builder().build();
        GetItemRequest request = GetItemRequest.builder().key(key).tableName(table).build();
        HashMap<String, String> parameters = new HashMap<String, String>();

        Map<String, AttributeValue> item = dynamoDb.getItem(request).item();
        LOGGER.debug("Item: " + item);

        if (item != null) {
            Map<String, String> variables = parseJson(item.get("Variables").s());
            LOGGER.debug("Variables: " + variables);

            variables.forEach(
                (column, value) -> parameters.put(column, value.toString())
            );
        }

        return parameters;
    }

    static Map<String, String> parseJson(String json) {
        Gson parser = new Gson();

        return parser.fromJson(json, HashMap.class);
    }
}
