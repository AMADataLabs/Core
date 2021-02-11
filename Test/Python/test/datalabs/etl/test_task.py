""" source: datalabs.etl.task """
import os

import mock
import pytest

import datalabs.etl.task as task


# pylint: disable=redefined-outer-name, protected-access
def test_etl_task(parameters):
    etl = task.ETLTask(parameters)

    etl.run()

    assert etl._extractor.data
    assert etl._transformer.data == 'True'
    assert etl._loader.data == 'True'


# pylint: disable=redefined-outer-name, protected-access, unused-argument
def test_etl_task_wrapper(environment_variables):
    with mock.patch('datalabs.access.parameter.aws.boto3'):
        wrapper = task.ETLTaskWrapper(task.ETLTask)

        wrapper.run()

    assert wrapper._task._extractor.data == 'True'
    assert wrapper._task._transformer.data == 'True'
    assert wrapper._task._loader.data == 'True'


@pytest.fixture
def parameters():
    return task.ETLParameters(
        extractor=task.ETLComponentParameters(
            variables=dict(CLASS='test.datalabs.etl.test_extract.Extractor', thing=True)
        ),
        transformer=task.ETLComponentParameters(
            variables=dict(CLASS='test.datalabs.etl.test_transform.Transformer')
        ),
        loader=task.ETLComponentParameters(
            variables=dict(CLASS='test.datalabs.etl.test_load.Loader')
        )
    )


@pytest.fixture
def environment_variables():
    current_env = os.environ.copy()

    os.environ['EXTRACTOR__TASK_CLASS'] = 'test.datalabs.etl.test_extract.Extractor'
    os.environ['EXTRACTOR__thing'] = 'True'

    os.environ['TRANSFORMER__TASK_CLASS'] = 'test.datalabs.etl.test_transform.Transformer'

    os.environ['LOADER__TASK_CLASS'] = 'test.datalabs.etl.test_load.Loader'
    os.environ['EXTRACTOR__DATABASE_HOST'] = 'ping.pong.com'

    yield os.environ

    os.environ.clear()
    os.environ.update(current_env)
