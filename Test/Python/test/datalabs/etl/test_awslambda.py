""" source: datalabs.etl.awslambda """
import os
import pytest

from   datalabs.etl.awslambda import ETLTaskWrapper, ETLException
from   datalabs.etl.task import ETLTask, ETLParameters, ETLComponentParameters


# pylint: disable=redefined-outer-name, protected-access
def test_task_wrapper_get_task_parameters(expected_parameters, event):
    wrapper = ETLTaskWrapper(dict())
    parameters = wrapper._get_task_parameters(event)

    assert expected_parameters == parameters


# pylint: disable=redefined-outer-name, protected-access
def test_task_wrapper_handle_exception():
    wrapper = ETLTaskWrapper(dict())
    status_code, body = wrapper._handle_exception(ETLException('failed'))

    assert status_code == 400
    assert body == dict(message='failed')


# pylint: disable=redefined-outer-name, protected-access
def test_task_wrapper_generate_response():
    wrapper = ETLTaskWrapper(dict())
    task = MockTask(None)
    status_code, body = wrapper._generate_response(task)

    assert status_code == 200
    assert body == dict()


class MockTask(ETLTask):
    def _run(self, session):
        pass


@pytest.fixture
def expected_parameters():
    return ETLParameters(
        extractor=ETLComponentParameters(
            database=dict(HOST='r2d2.droid.com'),
            variables=dict(CLASS='test.datalabs.etl.test_extract.Extractor', thing=True)
        ),
        transformer=ETLComponentParameters(
            database=dict(HOST='c3po.droid.com'),
            variables=dict(CLASS='test.datalabs.etl.test_transform.Transformer')
        ),
        loader=ETLComponentParameters(
            database=dict(HOST='l337.droid.com'),
            variables=dict(CLASS='test.datalabs.etl.test_load.Loader')
        )
    )


@pytest.fixture
def event():
    current_env = os.environ.copy()
    os.environ['EXTRACTOR_CLASS'] = 'test.datalabs.etl.test_extract.Extractor'
    os.environ['EXTRACTOR_thing'] = True
    os.environ['EXTRACTOR_DATABASE_HOST'] = 'r2d2.droid.com'
    os.environ['TRANSFORMER_CLASS'] = 'test.datalabs.etl.test_transform.Transformer'
    os.environ['TRANSFORMER_DATABASE_HOST'] = 'c3po.droid.com'
    os.environ['LOADER_CLASS'] = 'test.datalabs.etl.test_load.Loader'
    os.environ['LOADER_DATABASE_HOST'] = 'l337.droid.com'

    yield dict()

    os.environ = current_env
