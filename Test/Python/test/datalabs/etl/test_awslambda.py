""" source: datalabs.etl.awslambda """
import os

import mock
import pytest

from   datalabs.etl.awslambda import ETLTaskWrapper
import datalabs.etl.task as etl


# pylint: disable=redefined-outer-name, protected-access
def test_task_wrapper_get_task_parameters(expected_parameters, event):
    with mock.patch('datalabs.access.parameter.boto3') as mock_boto3:
        wrapper = ETLTaskWrapper(MockTask, parameters=event)
        parameters = wrapper._get_task_parameters()

    assert expected_parameters == parameters


# pylint: disable=redefined-outer-name, protected-access
def test_task_wrapper_handle_exception():
    with mock.patch('datalabs.access.parameter.boto3') as mock_boto3:
        wrapper = ETLTaskWrapper(MockTask)
        exception = etl.ETLException('failed')
        response = wrapper._handle_exception(exception)

    assert response == f'Failed: {str(exception)}'


# pylint: disable=redefined-outer-name, protected-access
def test_task_wrapper_generate_response():
    with mock.patch('datalabs.access.parameter.boto3') as mock_boto3:
        wrapper = ETLTaskWrapper(MockTask)
        response = wrapper._generate_response()

    assert response == "Success"


class MockTask(etl.ETLTask):
    def _run(self, session):
        pass


@pytest.fixture
def expected_parameters():
    return etl.ETLParameters(
        extractor=etl.ETLComponentParameters(
            database=dict(host='r2d2.droid.com'),
            variables=dict(
                CLASS='test.datalabs.etl.test_extract.Extractor',
                thing='True',
                EXECUTION_TIME='20200615T12:24:38+02:30',
                INCLUDENAMES='True'
            )
        ),
        transformer=etl.ETLComponentParameters(
            database=dict(host='c3po.droid.com'),
            variables=dict(
                CLASS='test.datalabs.etl.test_transform.Transformer',
                EXECUTION_TIME='20200615T12:24:38+02:30'
            )
        ),
        loader=etl.ETLComponentParameters(
            database=dict(host='l337.droid.com'),
            variables=dict(
                CLASS='test.datalabs.etl.test_load.Loader',
                EXECUTION_TIME='20200615T12:24:38+02:30'
            )
        )
    )


@pytest.fixture
def event():
    current_env = os.environ.copy()
    os.environ['EXTRACTOR_CLASS'] = 'test.datalabs.etl.test_extract.Extractor'
    os.environ['EXTRACTOR_thing'] = 'True'
    os.environ['EXTRACTOR_DATABASE_HOST'] = 'r2d2.droid.com'
    os.environ['EXTRACTOR_INCLUDENAMES'] = 'True'
    os.environ['TRANSFORMER_CLASS'] = 'test.datalabs.etl.test_transform.Transformer'
    os.environ['TRANSFORMER_DATABASE_HOST'] = 'c3po.droid.com'
    os.environ['LOADER_CLASS'] = 'test.datalabs.etl.test_load.Loader'
    os.environ['LOADER_DATABASE_HOST'] = 'l337.droid.com'

    yield dict(execution_time='20200615T12:24:38+02:30')

    os.environ.clear()
    os.environ.update(current_env)
