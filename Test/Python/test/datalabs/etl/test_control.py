""" source: datalabs.etl.control """
import json
import pandas
import pytest
import re

from   datalabs.etl.control import DAGNotificationFactoryTask


def test_parameters_parsed_correctly(data, parameters):
    factory = DAGNotificationFactoryTask({"dag": "DUMMY_DAG", "data": data})

    actual_parameters = factory._parse_iteration_parameters(data)

    assert all(parameters == actual_parameters)


def test_correct_messages_are_generated(parameters):
    factory = DAGNotificationFactoryTask({"dag": "DUMMY_DAG", "data": []})

    messages = factory._generate_notification_messages("DUMMY_DAG", parameters)

    assert len(messages) == 4
    for message in messages:
        assert "dag" in message
        assert re.match('DUMMY_DAG:[0-9]', message["dag"]) is not None
        assert "execution_time" in message
        assert "parameters" in message
        assert len(message["parameters"]) == 2


def test_messages_are_serialized_as_json_string(data, parameters):
    factory = DAGNotificationFactoryTask({"dag": "DUMMY_DAG", "data": data})

    output = factory._transform()

    assert len(output) == 1

    messages = json.loads(output[0])

    assert len(messages) == 4


@pytest.fixture
def data():
    return [
        b"""something,something_else
123,hello
456,there
""",
    b"""something,something_else
789,dear
135,john
"""
    ]


@pytest.fixture
def parameters():
    return pandas.DataFrame(
        data=dict(
            something=["123", "456", "789", "135"],
            something_else=["hello", "there", "dear", "john"]
        )
    )
