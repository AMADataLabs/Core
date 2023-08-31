package datalabs.etl.dag.aws;

import java.util.HashMap;
import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import datalabs.task.Task;
import datalabs.task.TaskException;


public class LambdaDagTaskWrapper extends AwsDagTaskWrapper {
    /* A DAG task wrapper for AWS Lambda function runtime environments.
     *
     * The DAG and task parameters are retrieved from a DynamoDB table. To boostrap the retrieval of these parameters,
     * an environment variable named DYNAMODB_CONFIG_TABLE contains the name of the DynamoDB configuration table.
     *
     * The DAG ID, task ID, and execution time are expected to be items in the Lambda event
     * ("dag", "task", and "execution_time" respectively). The Lambda event is passed directly as the task wrapper's
     * parameters.
     */
    static final Logger LOGGER = LoggerFactory.getLogger(LambdaDagTaskWrapper.class);

    public LambdaDagTaskWrapper(Map<String, String> environment, Map<String, String> parameters) {
        this.environment = environment;
        this.parameters = parameters;

        if ("DAG".equals(this.parameters.get("type"))) {
            throw new UnsupportedOperationException("DAG processing is not supported in Java.");
        }

        LOGGER.info("DAG: " + this.parameters.get("dag"));
        LOGGER.info("Task: " + this.parameters.get("task"));
        LOGGER.info("Execution Time: " + this.parameters.get("execution_time"));

        if (this.environment.get("DYNAMODB_CONFIG_TABLE") == null) {
            throw new IllegalArgumentException("DYNAMODB_CONFIG_TABLE environment variable is not set.");
        }
    }
}
