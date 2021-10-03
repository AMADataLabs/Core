''' Source: datalabs.etl.dag.awslambda '''
import os

import pytest

from   datalabs.etl.dag.awslambda import ProcessorTaskWrapper


# pylint: disable=redefined-outer-name, protected-access
def test_process_wrapper_sns_event_parsed_correctly(sns_event):
    wrapper = ProcessorTaskWrapper()
    parameters = wrapper._get_runtime_parameters(sns_event)

    assert len(parameters) == 3
    assert "dag" in parameters
    assert parameters["dag"] == "DAG_SCHEDULER"
    assert "task" in parameters
    assert parameters["task"] == "EXTRACT_SCHEDULE"
    assert "execution_time" in parameters
    assert parameters["execution_time"] == "2021-07-13T16:18:54.663464"


# pylint: disable=redefined-outer-name, protected-access
def test_process_wrapper_s3_event_parsed_correctly(s3_event):
    wrapper = ProcessorTaskWrapper()
    parameters = wrapper._get_runtime_parameters(s3_event)

    assert len(parameters) == 3
    assert "dag" in parameters
    assert parameters["dag"] == "DAG_SCHEDULER"
    assert "execution_time" in parameters
    assert hasattr(parameters["execution_time"], "upper")
    assert "task" in parameters
    assert parameters["task"] == "DAG"


# pylint: disable=redefined-outer-name, protected-access
def test_process_wrapper_cloudwatch_event_parsed_correctly(cloudwatch_event):
    wrapper = ProcessorTaskWrapper()
    parameters = wrapper._get_runtime_parameters(cloudwatch_event)

    assert len(parameters) == 3
    assert "dag" in parameters
    assert parameters["dag"] == "DAG_SCHEDULER"
    assert "execution_time" in parameters
    assert hasattr(parameters["execution_time"], "upper")
    assert "task" in parameters
    assert parameters["task"] == "DAG"


@pytest.mark.skipif(
    os.getenv('RUN_INTEGRATION_TESTS') != 'True',
    reason="Normally skip integration tests to increase testing speed."
)
# pylint: disable=redefined-outer-name, protected-access, unused-argument
def test_dag_processor_runs(environment, s3_event):
    os.environ['TASK_CLASS'] = 'datalabs.etl.dag.process.DAGProcessorTask'
    os.environ['DAG_CLASS'] = 'datalabs.etl.dag.schedule.dag.DAGSchedulerDAG'

    wrapper = ProcessorTaskWrapper(s3_event)

    wrapper.run()


@pytest.mark.skipif(
    os.getenv('RUN_INTEGRATION_TESTS') != 'True',
    reason="Normally skip integration tests to increase testing speed."
)
# pylint: disable=redefined-outer-name, protected-access, unused-argument
def test_task_processor_runs(environment, sns_event):
    os.environ['TASK_CLASS'] = 'datalabs.etl.dag.process.TaskProcessorTask'
    os.environ['DAG_CLASS'] = 'datalabs.etl.dag.schedule.dag.DAGSchedulerDAG'

    wrapper = ProcessorTaskWrapper(sns_event)

    wrapper.run()


@pytest.fixture
def runtime_parameters():
    return dict(
        dag="SOME_DAG",
        task="SOME_TASK",
        execution_time="2021-01-01T00:00:00.000000"
    )


@pytest.fixture
def sns_event():
    # pylint: disable=line-too-long
    return {
      'Records': [
        {
          'EventSource': 'aws:sns',
          'EventVersion': '1.0',
          'EventSubscriptionArn': 'arn:aws:sns:us-east-1:644454719059:DataLake-DAG-Processor-sbx:a7d72f53-e07f-44bd-aeae-db4787ab5c69',
          'Sns': {
            'Type': 'Notification',
            'MessageId': '807e8cdb-71aa-5bd5-a96c-d5835a102fb4',
            'TopicArn': 'arn:aws:sns:us-east-1:644454719059:DataLake-DAG-Processor-sbx',
            'Subject': None,
            'Message': '{"dag": "DAG_SCHEDULER", "task": "EXTRACT_SCHEDULE", "execution_time": "2021-07-13T16:18:54.663464"}',
            'Timestamp': '2021-07-01T20:45:46.090Z',
            'SignatureVersion': '1',
            'Signature': 'ZUwXyamt6MCEpZ3t5CwTU4FAEf1J9XXWLryq7PeLWQLz0tvIA5LvGdeB422XAo5qMUFXI7rhVJCZ+QWEB+OecVQ7w/9CCz/5Bf+VJhWWeW1Ip4UglHoG/kLHQeIxFdKX+GciNLsC0/gFc4uUdps2nl2U0fW2IkI4aKekyfXiFqm5MLpuropI0ss3pek6Qoyqb7zhLbMgVjdQgKJPhMaiAN4+sj9Y7trNOQX6z/WaE05c4JwgQc29zU8pKGXznrN90kHbDnwtspvHOACZf7FKH/kD6k6vjLJgF3b/BMTNAcU1NxTQte2lk1n2DMKnjFXyo6OxWj6ibETgtdq4zpWKkA==',
            'SigningCertUrl': 'https://sns.us-east-1.amazonaws.com/SimpleNotificationService-010a507c1833636cd94bdb98bd93083a.pem',
            'UnsubscribeUrl': 'https://sns.us-east-1.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:us-east-1:644454719059:DataLake-DAG-Processor-sbx:a7d72f53-e07f-44bd-aeae-db4787ab5c69',
            'MessageAttributes': {}
          }
        }
      ]
    }


@pytest.fixture
def s3_event():
    # pylint: disable=line-too-long
    return {
      "Records": [
        {
          "EventSource": "aws:sns",
          "EventVersion": "1.0",
          "EventSubscriptionArn": "arn:aws:sns:us-east-1:644454719059:DataLake-Scheduler-sbx:aad2653c-2522-4e67-90e1-c6a02105074a",
          "Sns": {
            "Type": "Notification",
            "MessageId": "0db70b4b-684c-5fea-a414-52290253b2f5",
            "TopicArn": "arn:aws:sns:us-east-1:644454719059:DataLake-Scheduler-sbx",
            "Subject": "Amazon S3 Notification",
            "Message": "{\"Records\":[{\"eventVersion\":\"2.1\",\"eventSource\":\"aws:s3\",\"awsRegion\":\"us-east-1\",\"eventTime\":\"2021-07-09T15:14:33.766Z\",\"eventName\":\"ObjectCreated:Put\",\"userIdentity\":{\"principalId\":\"AWS:AIDAZMDD6TZJ2T36WAMPX\"},\"requestParameters\":{\"sourceIPAddress\":\"76.244.141.27\"},\"responseElements\":{\"x-amz-request-id\":\"2YXSNHNRV6YJDR75\",\"x-amz-id-2\":\"2JwM0DFanD52zysJyG4ZuI818i6G5r/2Mcy5nqowHbLomYoir1jQMtt3tUIiApYgcRsRIG7MMvSh0tNOVWKb1XPqFBxgi/bamWAyj8dK18g=\"},\"s3\":{\"s3SchemaVersion\":\"1.0\",\"configurationId\":\"tf-s3-topic-20210702210724580200000003\",\"bucket\":{\"name\":\"ama-sbx-datalake-scheduler-data-us-east-1\",\"ownerIdentity\":{\"principalId\":\"A2VX7N7I5UQ0D9\"},\"arn\":\"arn:aws:s3:::ama-sbx-datalake-scheduler-data-us-east-1\"},\"object\":{\"key\":\"TEST\",\"size\":6556,\"eTag\":\"5c36a1b6d2fbcafb7de5ad6bbee7bcce\",\"versionId\":\"rLNvR267iZsX8c89P842bDjS19har6J2\",\"sequencer\":\"0060E867DE929A4400\"}}}]}",
            "Timestamp": "2021-07-09T15:14:39.600Z",
            "SignatureVersion": "1",
            "Signature": "RdJl6AJnXVtAz3uQlAgTl1RNSous22eXp62Ahy1Fq5zLAkWU9BYWw4AYZhs8AFLdKLE9Ybq0W4B0o63XFjs/MgT+UQNctA3KwI/Mr6bRzcV80MzXuVuoqRUyDa0N4HlODBFdO6NMx7CVIpkrTsn2WK+gSxy1YyXs1Nmn44n9FSCergj+IV++k/Uomu70Ah8Y9oZbg+AnLvm9r1c4j3BTsP+2n2xD2MNl5wSYCYEPoXhnewbX3DNst5ZgE3f/2AdEDyZH7lyY+KqI4Ew8LbsJz1zsEYkBekMwYkUulkrH+ylV+0RHSwww37sef3bNzaYXWXVSlZ3CEDdUdsSpiGyj0Q==",
            "SigningCertUrl": "https://sns.us-east-1.amazonaws.com/SimpleNotificationService-010a507c1833636cd94bdb98bd93083a.pem",
            "UnsubscribeUrl": "https://sns.us-east-1.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:us-east-1:644454719059:DataLake-Scheduler-sbx:aad2653c-2522-4e67-90e1-c6a02105074a",
            "MessageAttributes": {}
          }
        }
      ]
    }


@pytest.fixture
def cloudwatch_event():
    # pylint: disable=line-too-long
    return {
      "Records": [
        {
          "EventSource": "aws:sns",
          "EventVersion": "1.0",
          "EventSubscriptionArn": "arn:aws:sns:us-east-1:644454719059:DataLake-Scheduler-sbx:aad2653c-2522-4e67-90e1-c6a02105074a",
          "Sns": {
            "Type": "Notification",
            "MessageId": "0db70b4b-684c-5fea-a414-52290253b2f5",
            "TopicArn": "arn:aws:sns:us-east-1:644454719059:DataLake-Scheduler-sbx",
            "Subject": "Amazon S3 Notification",
            "Message": "{\"version\":\"0\",\"id\":\"24daf8cf-91d3-9d5f-dd03-8c4a40912597\",\"detail-type\":\"Scheduled Event\",\"source\":\"aws.events\",\"account\":\"644454719059\",\"time\":\"2021-09-17T20:45:00Z\",\"region\":\"us-east-1\",\"resources\":[\"arn:aws:events:us-east-1:644454719059:rule/DataLake-sbx-invoke-scheduler\"],\"detail\":{}}",
            "Timestamp": "2021-07-09T15:14:39.600Z",
            "SignatureVersion": "1",
            "Signature": "RdJl6AJnXVtAz3uQlAgTl1RNSous22eXp62Ahy1Fq5zLAkWU9BYWw4AYZhs8AFLdKLE9Ybq0W4B0o63XFjs/MgT+UQNctA3KwI/Mr6bRzcV80MzXuVuoqRUyDa0N4HlODBFdO6NMx7CVIpkrTsn2WK+gSxy1YyXs1Nmn44n9FSCergj+IV++k/Uomu70Ah8Y9oZbg+AnLvm9r1c4j3BTsP+2n2xD2MNl5wSYCYEPoXhnewbX3DNst5ZgE3f/2AdEDyZH7lyY+KqI4Ew8LbsJz1zsEYkBekMwYkUulkrH+ylV+0RHSwww37sef3bNzaYXWXVSlZ3CEDdUdsSpiGyj0Q==",
            "SigningCertUrl": "https://sns.us-east-1.amazonaws.com/SimpleNotificationService-010a507c1833636cd94bdb98bd93083a.pem",
            "UnsubscribeUrl": "https://sns.us-east-1.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:us-east-1:644454719059:DataLake-Scheduler-sbx:aad2653c-2522-4e67-90e1-c6a02105074a",
            "MessageAttributes": {}
          }
        }
      ]
    }


@pytest.fixture
def environment():
    current_env = os.environ.copy()

    os.environ['TASK_WRAPPER_CLASS'] = 'datalabs.etl.dag.awslambda.ProcessorTaskWrapper'
    os.environ['DYNAMODB_CONFIG_TABLE'] = 'DataLake-configuration-sbx'

    yield os.environ

    os.environ.clear()
    os.environ.update(current_env)
