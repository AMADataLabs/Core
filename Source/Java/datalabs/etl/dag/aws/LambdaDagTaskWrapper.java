package datalabs.etl.dag.aws;

import java.util.HashMap;
import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import datalabs.task.Task;
import datalabs.task.TaskException;


public class LambdaDagTaskWrapper extends AwsDagTaskWrapper {
    static final Logger LOGGER = LoggerFactory.getLogger(LambdaDagTaskWrapper.class);

    public LambdaDagTaskWrapper(Map<String, String> environment, Map<String, String> parameters) {
        super(environment, parameters);
    }

    protected Map<String, String> getRuntimeParameters(Map<String, String> parameters) throws TaskException {
        HashMap<String, String> runtimeParameters = null;

        try {
            if ("DAG".equals(parameters.get("type"))) {
                throw new UnsupportedOperationException("DAG processing is not supported in Java.");
            }

            LOGGER.info("DAG: " + parameters.get("dag"));
            LOGGER.info("Task: " + parameters.get("task"));
            LOGGER.info("Execution Time: " + parameters.get("execution_time"));

            runtimeParameters = new HashMap<String, String>() {{
                putAll(getDagParameters(parameters.get("dag")));
                putAll(parameters);
            }};
        } catch (Exception exception) {
            throw new TaskException("Unable to get runtime parameters.", exception);
        }

        return runtimeParameters;
    }
}