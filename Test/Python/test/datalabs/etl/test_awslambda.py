""" source: datalabs.etl.awslambda """
import os
import pytest

from   datalabs.etl.awslambda import ETLTaskWrapper
import datalabs.etl.task as etl


# pylint: disable=redefined-outer-name, protected-access
def test_task_wrapper_get_task_parameters(expected_parameters, event):
    wrapper = ETLTaskWrapper(MockTask, parameters=event)
    parameters = wrapper._get_task_parameters()

    assert expected_parameters == parameters


# pylint: disable=redefined-outer-name, protected-access
def test_task_wrapper_handle_exception():
    wrapper = ETLTaskWrapper(MockTask)
    status_code, headers, body = wrapper._handle_exception(etl.ETLException('failed'))

    assert status_code == 400
    assert headers == dict()
    assert body == dict(message='failed')


# pylint: disable=redefined-outer-name, protected-access
def test_task_wrapper_generate_response():
    wrapper = ETLTaskWrapper(MockTask)
    status_code, headers, body = wrapper._generate_response()

    assert status_code == 200
    assert headers == dict()
    assert body == dict()


class MockTask(etl.ETLTask):
    def _run(self, session):
        pass


@pytest.fixture
def expected_parameters():
    return etl.ETLParameters(
        extractor=etl.ETLComponentParameters(
            database=dict(HOST='r2d2.droid.com'),
            variables=dict(CLASS='test.datalabs.etl.test_extract.Extractor', thing='True')
        ),
        transformer=etl.ETLComponentParameters(
            database=dict(HOST='c3po.droid.com'),
            variables=dict(CLASS='test.datalabs.etl.test_transform.Transformer')
        ),
        loader=etl.ETLComponentParameters(
            database=dict(HOST='l337.droid.com'),
            variables=dict(CLASS='test.datalabs.etl.test_load.Loader')
        )
    )


@pytest.fixture
def event():
    current_env = os.environ.copy()
    os.environ['EXTRACTOR_CLASS'] = 'test.datalabs.etl.test_extract.Extractor'
    os.environ['EXTRACTOR_thing'] = 'True'
    os.environ['EXTRACTOR_DATABASE_HOST'] = 'r2d2.droid.com'
    os.environ['TRANSFORMER_CLASS'] = 'test.datalabs.etl.test_transform.Transformer'
    os.environ['TRANSFORMER_DATABASE_HOST'] = 'c3po.droid.com'
    os.environ['LOADER_CLASS'] = 'test.datalabs.etl.test_load.Loader'
    os.environ['LOADER_DATABASE_HOST'] = 'l337.droid.com'

    yield os.environ

    os.environ.clear()
    os.environ.update(current_env)
