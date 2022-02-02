package datalabs.access.parameter;

import java.util.HashMap;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

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

    public void load(Map<String, String> environment) {
        Map<String, String> globalVariables = getParametersFromDynamoDb("GLOBAL");
        Map<String, String> parameters = getParametersFromDynamoDB(this.task);

        ReferenceEnvironmentLoader(globalVariables).load(environment=parameters);

        environment.putAll(parameters);
    }

    Map<String, String> getParametersFromDynamoDB(String task) {
        DynamoDbClient dynamoDb = DynamoDbClient.builder().build();
        Map<String, AttributeValue> key = this.getKey(task);
        Map<String, String> parameters = null;

        try {
            parameters = DynamoDbEnvironmentLoader.getRowFromTable(this.table, key);
        } catch (DynamoDbException e) {
            System.err.println(e.getMessage());
            System.exit(1);
        }

        return parameters;
    }

    HashMap<String, AttributeValue> getKey(String task) {
        return new HashMap<String, AttributeValue>() {{
            put("DAG", AttributeValue.builder().s(this.dag).build());
            put("Task", AttributeValue.builder().s(task).build());
        }};
    }

    Map<String, String> getItemFromTable(String table, Map<String, AttributeValue> key) throws DynamoDbException{
        GetItemRequest request = GetItemRequest.builder().key(key).tableName(this.table).build();
        HashMap<String, String> parameters = new HashMap<String, String>();

        Map<String, AttributeValue> item = dynamodb.getItem(request).item();

        if (item == null) {
            throw IllegalArgumentException("Not data in DynamoDB table \"" + table + "\" for the given key.");
        }

        item.forEach(
            (column, value) -> parameters.put(column, value.toString())
        );

        return parameters;
    }
}


// class DynamoDBEnvironmentLoader(ParameterValidatorMixin):
//     PARAMETER_CLASS = DynamoDBParameters
//
//
//     def _get_parameters_from_dynamodb(self, task):
//         response = None
//
//         with AWSClient("dynamodb") as dynamodb:
//             response = dynamodb.get_item(
//                 TableName=self._parameters.table,
//                 Key=dict(
//                     DAG=dict(S=self._parameters.dag),
//                     Task=dict(S=task)
//                 )
//             )
//
//         return self._extract_parameters(response)
//
//     @classmethod
//     def _extract_parameters(cls, response):
//         parameters = {}
//
//         if "Item" in response:
//             if "Variables" not in response["Item"]:
//                 raise ValueError(f'Invalid DynamoDB configuration item: {json.dumps(response)}')
//
//             parameters = json.loads(response["Item"]["Variables"]["S"])
//
//         return parameters
