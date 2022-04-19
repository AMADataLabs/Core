package datalabs.etl.dag.notify.sns;

import java.lang.reflect.InvocationTargetException;
import java.util.HashMap;
import java.util.Map;

import software.amazon.awssdk.services.sns.SnsClient;
import software.amazon.awssdk.services.sns.model.PublishRequest;

import datalabs.etl.dag.state.Status;
import datalabs.parameter.Parameters;
import datalabs.plugin.PluginImporter;


public class DagNotifier {
    String topicArn;

    public DagNotifier(String topicArn) {
        this.topicArn = topicArn;
    }

    public void notify(String dag, String executionTime) {
        SnsClient sns = SnsClient.builder().build();
        PublishRequest request = PublishRequest.builder().targetArn(
            this.topicArn
        ).message(
            "{\"dag\": \"" + dag + "\", \"execution_time\": \"" + executionTime + "\"}"
        ).build();

        sns.publish(request);
    }
}
