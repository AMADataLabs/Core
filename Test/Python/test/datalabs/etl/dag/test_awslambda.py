''' Source: datalabs.etl.dag.awslambda '''
from   functools import partial
import os
import mock

import pytest

from   datalabs.task import Task
from   datalabs.etl.dag import DAG
from   datalabs.etl.dag.awslambda import ProcessorTaskWrapper


# pylint: disable=redefined-outer-name, protected-access
def test_process_wrapper_dag_event_parsed_correctly(dag_event, get_dag_task_parameters_from_dynamodb):
    wrapper = ProcessorTaskWrapper(dag_event)

    with mock.patch.object(
        ProcessorTaskWrapper,
        '_get_dag_task_parameters_from_dynamodb',
        new=get_dag_task_parameters_from_dynamodb
    ):
        parameters = wrapper._get_task_parameters()

    assert len(parameters) == 4
    assert parameters.get("dag") == "DAG_SCHEDULER"
    assert parameters.get("DAG_CLASS") == "SOME_DAG"
    assert parameters.get("execution_time") == "2021-07-13T16:18:54.663464"
    assert parameters.get("DAG_STATE") == '{"CLASS": "foo"}'


# pylint: disable=redefined-outer-name, protected-access
def test_process_wrapper_task_event_parsed_correctly(task_event, get_dag_task_parameters_from_dynamodb):
    wrapper = ProcessorTaskWrapper(task_event)

    with mock.patch.object(
        ProcessorTaskWrapper,
        '_get_dag_task_parameters_from_dynamodb',
        new=get_dag_task_parameters_from_dynamodb
    ):
        parameters = wrapper._get_task_parameters()

    assert len(parameters) == 6
    assert parameters.get("dag") == "DAG_SCHEDULER"
    assert parameters.get("task") == "EXTRACT_SCHEDULE"
    assert parameters.get("execution_time") == "2021-07-13T16:18:54.663464"
    assert parameters.get("DAG_STATE") == '{"CLASS": "foo"}'


# pylint: disable=redefined-outer-name, protected-access, unused-argument
def test_process_wrapper_scheduler_event_parsed_correctly(scheduler_event, get_dag_task_parameters_from_dynamodb):
    wrapper = ProcessorTaskWrapper(scheduler_event)

    with mock.patch.object(
        ProcessorTaskWrapper,
        '_get_dag_task_parameters_from_dynamodb',
        new=partial(get_dag_task_parameters_from_dynamodb, ProcessorTaskWrapper)
    ):
        parameters = wrapper._get_task_parameters()

    assert len(parameters) == 4
    assert "handler_class" in parameters
    assert parameters["handler_class"] == "datalabs.etl.dag.trigger.handler.scheduler.TriggerHandlerTask"
    assert "dag_topic_arn" in parameters
    assert parameters["dag_topic_arn"] == "arn:aws:sns:us-east-1:644454719059:DataLake-sbx-DAGPRocessor"
    assert "event" in parameters
    assert hasattr(parameters["event"], "items")


@pytest.mark.skipif(
    os.getenv('RUN_INTEGRATION_TESTS') != 'True',
    reason="Normally skip integration tests to increase testing speed."
)
# pylint: disable=redefined-outer-name, protected-access, unused-argument
def test_dag_processor_runs(environment, scheduler_event):
    os.environ['TASK_CLASS'] = 'datalabs.etl.dag.process.DAGProcessorTask'
    os.environ['DAG_CLASS'] = 'datalabs.etl.dag.schedule.dag.DAGSchedulerDAG'

    wrapper = ProcessorTaskWrapper(scheduler_event)

    wrapper.run()


@pytest.mark.skipif(
    os.getenv('RUN_INTEGRATION_TESTS') != 'True',
    reason="Normally skip integration tests to increase testing speed."
)
# pylint: disable=redefined-outer-name, protected-access, unused-argument
def test_task_processor_runs(environment, dag_event):
    os.environ['TASK_CLASS'] = 'datalabs.etl.dag.process.TaskProcessorTask'
    os.environ['DAG_CLASS'] = 'datalabs.etl.dag.schedule.dag.DAGSchedulerDAG'

    wrapper = ProcessorTaskWrapper(dag_event)

    wrapper.run()


class MockTask(Task):
    def run(self):
        pass


class MockDAG(DAG):
    def run(self):
        pass


@pytest.fixture
def environment():
    current_env = os.environ.copy()

    os.environ['TASK_WRAPPER_CLASS'] = 'datalabs.etl.dag.awslambda.ProcessorTaskWrapper'
    os.environ['DYNAMODB_CONFIG_TABLE'] = 'DataLake-configuration-sbx'

    yield os.environ

    os.environ.clear()
    os.environ.update(current_env)


@pytest.fixture
def dag_parameters():
    return dict(
        DAG_CLASS="SOME_DAG",
        DAG_STATE='{"CLASS": "foo"}'
    )


@pytest.fixture
def task_parameters():
    return dict(
        TASK_CLASS='test.datalabs.etl.dag.test_awslambda.MockTask',
        DAG_STATE='{"CLASS": "bar"}'
    )


@pytest.fixture
def trigger_parameters():
    return dict(
        HANDLER_CLASS="datalabs.etl.dag.trigger.handler.scheduler.TriggerHandlerTask",
        DAG_TOPIC_ARN="arn:aws:sns:us-east-1:644454719059:DataLake-sbx-DAGPRocessor"
    )


@pytest.fixture
def get_dag_task_parameters_from_dynamodb(dag_parameters, task_parameters, trigger_parameters):
    # pylint: disable=unused-argument
    def _get_dag_task_parameters_from_dynamodb(cls, dag, task, execution_time=None):
        parameters = {}

        if task == "DAG":
            parameters = dag_parameters
        elif task in ("HANDLER", "Scheduler"):
            parameters = trigger_parameters
        else:
            parameters = task_parameters

        return parameters

    return _get_dag_task_parameters_from_dynamodb


@pytest.fixture
def dag_event(environment):
    # pylint: disable=line-too-long
    return {
      'Records': [
        {
          'EventSource': 'aws:sns',
          'EventVersion': '1.0',
          'EventSubscriptionArn': 'arn:aws:sns:us-east-1:644454719059:DataLake-sbx-DAGProcessor:a7d72f53-e07f-44bd-aeae-db4787ab5c69',
          'Sns': {
            'Type': 'Notification',
            'MessageId': '807e8cdb-71aa-5bd5-a96c-d5835a102fb4',
            'TopicArn': 'arn:aws:sns:us-east-1:644454719059:DataLake-sbx-DAGProcessor',
            'Subject': None,
            'Message': '{"dag": "DAG_SCHEDULER", "execution_time": "2021-07-13T16:18:54.663464"}',
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
def task_event(environment):
    # pylint: disable=line-too-long
    return {
      'Records': [
        {
          'EventSource': 'aws:sns',
          'EventVersion': '1.0',
          'EventSubscriptionArn': 'arn:aws:sns:us-east-1:644454719059:DataLake-sbx-DAGProcessor:a7d72f53-e07f-44bd-aeae-db4787ab5c69',
          'Sns': {
            'Type': 'Notification',
            'MessageId': '807e8cdb-71aa-5bd5-a96c-d5835a102fb4',
            'TopicArn': 'arn:aws:sns:us-east-1:644454719059:DataLake-sbx-TaskProcessor',
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
def scheduler_event(environment):
    # pylint: disable=line-too-long
    return {
      "Records": [
        {
          "EventSource": "aws:sns",
          "EventVersion": "1.0",
          "EventSubscriptionArn": "arn:aws:sns:us-east-1:644454719059:DataLake-sbx-Scheduler:aad2653c-2522-4e67-90e1-c6a02105074a",
          "Sns": {
            "Type": "Notification",
            "MessageId": "0db70b4b-684c-5fea-a414-52290253b2f5",
            "TopicArn": "arn:aws:sns:us-east-1:644454719059:DataLake-sbx-Scheduler",
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
