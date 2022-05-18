package datalabs.etl.dag.aws;

import java.util.HashMap;
import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import datalabs.task.Task;


public class LambdaDagTaskWrapper extends AwsDagTaskWrapper {
    static final Logger LOGGER = LoggerFactory.getLogger(LambdaDagTaskWrapper.class);

    public LambdaDagTaskWrapper(Map<String, String> environment, Map<String, String> parameters) {
        super(environment, parameters);
    }

    protected Map<String, String> getRuntimeParameters(Map<String, String> parameters) {
        if ("DAG".equals(parameters.get("type"))) {
            throw new UnsupportedOperationException("DAG processing is not supported in Java.");
        }

        HashMap<String, String> runtimeParameters = new HashMap<String, String>() {{
            putAll(getDagParameters(parameters.get("dag")));
            putAll(parameters);
        }};

        return runtimeParameters;
    }
}
