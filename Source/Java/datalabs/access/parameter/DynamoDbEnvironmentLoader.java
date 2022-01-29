package datalabs.access.parameter;

import java.util.HashMap;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.apache.logging.log4j.Logger;
import org.apache.logging.log4j.LogManager;

import datalabs.access.parameter.ReferenceEnvironmentLoader;


public class DynamoDbEnvironmentLoader {
    protected static final Logger LOGGER = LogManager.getLogger();

    Map<String, String> parameters;
}


// class DynamoDBEnvironmentLoader(ParameterValidatorMixin):
//     PARAMETER_CLASS = DynamoDBParameters
//
//     def __init__(self, parameters):
//         self._parameters = self._get_validated_parameters(parameters)
//
//     def load(self, environment: dict = None):
//         if environment is None:
//             environment = os.environ
//         global_variables = self._get_parameters_from_dynamodb("GLOBAL")
//
//         parameters = self._get_parameters_from_dynamodb(self._parameters.task)
//
//         ReferenceEnvironmentLoader(global_variables).load(environment=parameters)
//
//         environment.update(parameters)
//
//     @classmethod
//     def from_environ(cls):
//         table = os.environ.get('DYNAMODB_CONFIG_TABLE')
//         dag = os.environ.get('DYNAMODB_CONFIG_DAG')
//         task = os.environ.get('DYNAMODB_CONFIG_TASK')
//         loader = None
//
//         if table and dag and task:
//             loader = DynamoDBEnvironmentLoader(dict(table=table, dag=dag, task=task))
//
//         return loader
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
