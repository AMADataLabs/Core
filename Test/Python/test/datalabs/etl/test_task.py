""" source: datalabs.etl.task """
from   dataclasses import dataclass
import os

import mock
import pytest

from   datalabs.etl import task
from   datalabs.parameter import add_schema


# pylint: disable=redefined-outer-name, protected-access
def test_etl_task(parameters):
    etl = task.ETLTask(parameters)

    etl.run()

    assert etl._output.extractor == [b'True']
    assert etl._output.transformer == [b'True']
    assert etl._output.loader == [b'True']


# pylint: disable=redefined-outer-name, protected-access, unused-argument
def test_etl_task_wrapper(environment_variables):
    with mock.patch('datalabs.access.parameter.aws.boto3'):
        wrapper = task.ETLTaskWrapper(task.ETLTask)

        wrapper.run()

    assert wrapper.task._output.extractor == [b'True']
    assert wrapper.task._output.transformer == [b'True']
    assert wrapper.task._output.loader == [b'True']


def test_get_validated_parameters_returns_proper_object(parameters):
    parameters["transformer"].pop('TASK_CLASS')
    task = DummyTask(parameters["transformer"])

    assert isinstance(task._parameters, TaskParameters)
    assert hasattr(task._parameters, 'cooley')
    assert task._parameters.cooley == 'Boyz'
    assert hasattr(task._parameters, 'high')
    assert task._parameters.high == 'II'
    assert hasattr(task._parameters, 'harmony')
    assert task._parameters.harmony == 'Men'


def test_get_validated_parameters_preserves_input_data(parameters):
    parameters["transformer"].pop('TASK_CLASS')
    task = DummyTask(parameters["transformer"], ['East', 'Coast', 'Family'])

    assert isinstance(task._parameters, TaskParameters)
    assert task._data == ['East', 'Coast', 'Family']


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class TaskParameters:
    cooley: str
    high: str
    harmony: str


class DummyTask(task.Task):
    PARAMETER_CLASS = TaskParameters

    def run(self):
        return [b'True']


@pytest.fixture
def parameters():
    return dict(
        extractor=dict(
            TASK_CLASS='test.datalabs.etl.test_task.DummyTask',
            COOLEY='Boyz',
            HIGH='II',
            HARMONY='Men'
        ),
        transformer=dict(
            TASK_CLASS='test.datalabs.etl.test_task.DummyTask',
            COOLEY='Boyz',
            HIGH='II',
            HARMONY='Men'
        ),
        loader=dict(
            TASK_CLASS='test.datalabs.etl.test_task.DummyTask',
            COOLEY='Boyz',
            HIGH='II',
            HARMONY='Men'
        )
    )


# pylint: disable=too-many-statements
@pytest.fixture
def environment_variables():
    current_env = os.environ.copy()

    os.environ['TASK_CLASS'] = 'datalabs.etl.task.ETLTask'

    os.environ['EXTRACTOR__TASK_CLASS'] = 'test.datalabs.etl.test_task.DummyTask'
    os.environ['EXTRACTOR__COOLEY'] = 'Boyz'
    os.environ['EXTRACTOR__HIGH'] = 'II'
    os.environ['EXTRACTOR__HARMONY'] = 'Men'

    os.environ['TRANSFORMER__TASK_CLASS'] = 'test.datalabs.etl.test_task.DummyTask'
    os.environ['TRANSFORMER__COOLEY'] = 'Boyz'
    os.environ['TRANSFORMER__HIGH'] = 'II'
    os.environ['TRANSFORMER__HARMONY'] = 'Men'

    os.environ['LOADER__TASK_CLASS'] = 'test.datalabs.etl.test_task.DummyTask'
    os.environ['LOADER__COOLEY'] = 'Boyz'
    os.environ['LOADER__HIGH'] = 'II'
    os.environ['LOADER__HARMONY'] = 'Men'

    yield os.environ

    os.environ.clear()
    os.environ.update(current_env)
