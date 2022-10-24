""" source: datalabs.etl.control """
import json
import re

import pandas
import pytest

from   datalabs.etl.control import DAGNotificationFactoryTask


# pylint: disable=redefined-outer-name, protected-access
def test_parameters_parsed_correctly(data, parameters):
    factory = DAGNotificationFactoryTask({"dag": "DUMMY_DAG", "execution_time": "2022-05-19 00:00:00"}, data)

    actual_parameters = factory._parse_iteration_parameters(data)

    assert all(parameters == actual_parameters)


# pylint: disable=redefined-outer-name, protected-access
def test_correct_messages_are_generated(parameters):
    factory = DAGNotificationFactoryTask({"dag": "DUMMY_DAG", "execution_time": "2022-05-19 00:00:00"}, [])

    messages = factory._generate_notification_messages("DUMMY_DAG", "2022-05-19 00:00:00", parameters)

    assert len(messages) == 4
    for message in messages:
        assert "dag" in message
        assert re.match('DUMMY_DAG:[0-9]', message["dag"]) is not None
        assert "execution_time" in message
        assert "parameters" in message
        assert len(message["parameters"]) == 2


# pylint: disable=redefined-outer-name, protected-access
def test_messages_are_serialized_as_json_string(data):
    factory = DAGNotificationFactoryTask({"dag": "DUMMY_DAG", "execution_time": "2022-05-19 00:00:00"}, data)

    output = factory.run()

    assert len(output) == 1

    messages = json.loads(output[0].decode())

    assert len(messages) == 4

# pylint: disable=redefined-outer-name, protected-access
def test_empty_parameters():
    iteration_parameters = pandas.DataFrame()

    messages = DAGNotificationFactoryTask._generate_notification_messages(
        "DUMMY_DAG",
        "2022-05-19 00:00:00",
        iteration_parameters
    )

    assert len(messages) == 1
    assert len(messages[0]) == 2
    assert "dag" in messages[0]
    assert messages[0]["dag"] == "DUMMY_DAG"
    assert "execution_time" in messages[0]
    assert messages[0]["execution_time"] == "2022-05-19 00:00:00"

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
