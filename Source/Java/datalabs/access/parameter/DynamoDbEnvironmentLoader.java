package datalabs.access.parameter;

import java.util.HashMap;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.apache.logging.log4j.Logger;
import org.apache.logging.log4j.LogManager;
import software.amazon.awssdk.services.dynamodb.DynamoDbClient;

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

        ReferenceEnvironmentLoader(globalVariables).load(environment=parameters)

        environment.putAll(parameters);
    }

    Map<String, String> getParametersFromDynamoDB(String task) {
        DynamoDbClient dynamoDb = DynamoDbClient.builder().build();

        HashMap<String, AttributeValue> key = new HashMap<String, AttributeValue>() {{
            put("DAG", AttributeValue.builder().s(this.dag).build());
            put("Task", AttributeValue.builder().s(task).build());
        }};

        GetItemRequest request = GetItemRequest.builder().key(key).tableName(this.table).build();

        // try {
        //     Map<String,AttributeValue> returnedItem = ddb.getItem(request).item();
        //
        //     if (returnedItem != null) {
        //         Set<String> keys = returnedItem.keySet();
        //         System.out.println("Amazon DynamoDB table attributes: \n");
        //
        //         for (String key1 : keys) {
        //             System.out.format("%s: %s\n", key1, returnedItem.get(key1).toString());
        //         }
        //     } else {
        //         System.out.format("No item found with the key %s!\n", key);
        //     }
        // } catch (DynamoDbException e) {
        //     System.err.println(e.getMessage());
        //     System.exit(1);
        // }
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
