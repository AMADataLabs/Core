""" source: datalabs.etl.task """
import os
import pytest

import datalabs.etl.task as task


# pylint: disable=redefined-outer-name, protected-access
def test_etl_task(parameters):
    etl = task.ETLTask(parameters)

    etl.run()

    assert etl._extractor.data
    assert etl._transformer.data == 'True'
    assert etl._loader.data == 'True'


# pylint: disable=redefined-outer-name, protected-access
def test_etl_task_wrapper(environment_variables):
    wrapper = task.ETLTaskWrapper(task.ETLTask)

    wrapper.run()

    assert wrapper._task._extractor.data == 'True'
    assert wrapper._task._transformer.data == 'True'
    assert wrapper._task._loader.data == 'True'


@pytest.fixture
def parameters():
    return task.ETLParameters(
        extractor=task.ETLComponentParameters(
            database={},
            variables=dict(CLASS='test.datalabs.etl.test_extract.Extractor', thing=True)
        ),
        transformer=task.ETLComponentParameters(
            database={},
            variables=dict(CLASS='test.datalabs.etl.test_transform.Transformer')
        ),
        loader=task.ETLComponentParameters(
            database={},
            variables=dict(CLASS='test.datalabs.etl.test_load.Loader')
        )
    )


@pytest.fixture
def environment_variables():
    current_env = os.environ.copy()

    os.environ['EXTRACTOR_CLASS'] = 'test.datalabs.etl.test_extract.Extractor'
    os.environ['EXTRACTOR_thing'] = 'True'

    os.environ['TRANSFORMER_CLASS'] = 'test.datalabs.etl.test_transform.Transformer'

    os.environ['LOADER_CLASS'] = 'test.datalabs.etl.test_load.Loader'
    os.environ['EXTRACTOR_DATABASE_HOST'] = 'ping.pong.com'

    yield os.environ

    os.environ.clear()
    os.environ.update(current_env)
