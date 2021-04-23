""" source: datalabs.etl.task """
from   dataclasses import dataclass
import os

import mock
import pytest

import datalabs.etl.task as task
from   datalabs.task import add_schema


# pylint: disable=redefined-outer-name, protected-access
def test_etl_task(parameters):
    etl = task.ETLTask(parameters)

    etl.run()

    assert etl._extractor.data
    assert etl._transformer.data == 'True'
    assert etl._loader.data is None


# pylint: disable=redefined-outer-name, protected-access, unused-argument
def test_etl_task_wrapper(environment_variables):
    with mock.patch('datalabs.access.parameter.aws.boto3'):
        wrapper = task.ETLTaskWrapper(task.ETLTask)

        wrapper.run()

    assert wrapper.task._extractor.data == 'True'
    assert wrapper.task._transformer.data == 'True'
    assert wrapper.task._loader.data is None


def test_get_validated_parameters_returns_proper_object(parameters):
    parameters.transformer.pop('TASK_CLASS')
    task = DummyTask(parameters.transformer)

    assert isinstance(task._parameters, TaskParameters)
    assert hasattr(task._parameters, 'cooley')
    assert task._parameters.cooley == 'Boyz'
    assert hasattr(task._parameters, 'high')
    assert task._parameters.high == 'II'
    assert hasattr(task._parameters, 'harmony')
    assert task._parameters.harmony == 'Men'


def test_get_validated_parameters_preserves_input_data(parameters):
    parameters.transformer.pop('TASK_CLASS')
    parameters.transformer['data'] = ['East', 'Coast', 'Family']
    task = DummyTask(parameters.transformer)

    assert isinstance(task._parameters, TaskParameters)
    assert hasattr(task._parameters, 'data')
    assert task._parameters.data == ['East', 'Coast', 'Family']


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class TaskParameters:
    cooley: str
    high: str
    harmony: str
    data: object = None


class DummyTask(task.ETLComponentTask):
    PARAMETER_CLASS = TaskParameters

    def run(self):
        self._data = self._parameters['data']


@pytest.fixture
def parameters():
    return task.ETLParameters(
        extractor=dict(
            TASK_CLASS='test.datalabs.etl.test_extract.Extractor',
            thing=True
        ),
        transformer=dict(
            TASK_CLASS='test.datalabs.etl.test_transform.Transformer',
            COOLEY='Boyz',
            HIGH='II',
            HARMONY='Men'
        ),
        loader=dict(TASK_CLASS='test.datalabs.etl.test_load.Loader')
    )


@pytest.fixture
def environment_variables():
    current_env = os.environ.copy()

    os.environ['TASK_CLASS'] = 'datalabs.etl.task.ETLTask'

    os.environ['EXTRACTOR__TASK_CLASS'] = 'test.datalabs.etl.test_extract.Extractor'
    os.environ['EXTRACTOR__thing'] = 'True'

    os.environ['TRANSFORMER__TASK_CLASS'] = 'test.datalabs.etl.test_transform.Transformer'
    os.environ['TRANSFORMER__COOLEY'] = 'Boyz'
    os.environ['TRANSFORMER__HIGH'] = 'II'
    os.environ['TRANSFORMER__HARMONY'] = 'Men'

    os.environ['LOADER__TASK_CLASS'] = 'test.datalabs.etl.test_load.Loader'
    os.environ['EXTRACTOR__DATABASE_HOST'] = 'ping.pong.com'

    yield os.environ

    os.environ.clear()
    os.environ.update(current_env)
