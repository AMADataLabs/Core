import os
import pytest

from   datalabs.etl.awslambda import ETLTaskWrapper, ETLException
from   datalabs.etl.task import ETLTask, ETLParameters


def test_task_wrapper_get_task_parameters(expected_parameters, event):
    wrapper = ETLTaskWrapper(dict())
    parameters = wrapper._get_task_parameters(event)

    assert expected_parameters == parameters


def test_task_wrapper_handle_exception():
    wrapper = ETLTaskWrapper(dict())
    status_code, body = wrapper._handle_exception(ETLException('failed'))

    assert status_code == 400
    assert body == dict(message='failed')


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
        extractor=dict(CLASS='test.datalabs.etl.test_extract.Extractor', thing=True),
        transformer=dict(CLASS='test.datalabs.etl.test_transform.Transformer'),
        loader=dict(CLASS='test.datalabs.etl.test_load.Loader'),
    )


@pytest.fixture
def event():
    current_env = os.environ.copy()
    os.environ['EXTRACTOR_CLASS'] = 'test.datalabs.etl.test_extract.Extractor'
    os.environ['EXTRACTOR_thing'] = True
    os.environ['TRANSFORMER_CLASS'] = 'test.datalabs.etl.test_transform.Transformer'
    os.environ['LOADER_CLASS'] = 'test.datalabs.etl.test_load.Loader'

    yield dict()

    os.environ = current_env
