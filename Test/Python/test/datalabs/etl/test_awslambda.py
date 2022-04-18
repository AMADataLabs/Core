""" source: datalabs.etl.awslambda """
import logging
import os

import mock
import pytest

from   datalabs.etl.awslambda import ETLTaskWrapper
import datalabs.etl.task as etl

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=redefined-outer-name, protected-access
def test_task_wrapper_get_task_parameters(expected_parameters, event):
    with mock.patch('datalabs.access.parameter.aws.boto3'):
        with mock.patch('datalabs.access.secret.aws.boto3'):
            wrapper = ETLTaskWrapper(parameters=event)
            wrapper._setup_environment()
            parameters = wrapper._get_task_parameters()
            LOGGER.debug(parameters)

    assert expected_parameters == parameters


# pylint: disable=redefined-outer-name, protected-access
def test_task_wrapper_handle_exception():
    with mock.patch('datalabs.access.parameter.aws.boto3'):
        with mock.patch('datalabs.access.secret.aws.boto3'):
            wrapper = ETLTaskWrapper()
            exception = etl.ETLException('failed')
            response = wrapper._handle_exception(exception)

    assert response == f'Failed: {str(exception)}'


# pylint: disable=redefined-outer-name, protected-access
def test_task_wrapper_handle_success():
    with mock.patch('datalabs.access.parameter.aws.boto3'):
        with mock.patch('datalabs.access.secret.aws.boto3'):
            wrapper = ETLTaskWrapper()
            response = wrapper._handle_success()

    assert response == "Success"


class MockTask(etl.ETLTask):
    def _run(self, session):
        pass


@pytest.fixture
def expected_parameters():
    return etl.ETLParameters(
        extractor=dict(
            TASK_CLASS='test.datalabs.etl.test_extract.Extractor',
            thing='True',
            EXECUTION_TIME='20200615T12:24:38+02:30',
            INCLUDE_NAMES='True',
            DATABASE_HOST='r2d2.droid.com',
            DATABASE_PORT='5432',
            DATABASE_NAME='mydatabase',
            DATABASE_BACKEND='postgresql+psycopg2',
            DATABASE_USERNAME='mrkitty',
            DATABASE_PASSWORD='prettyboy59'
        ),
        transformer=dict(
            TASK_CLASS='test.datalabs.etl.test_transform.Transformer',
            EXECUTION_TIME='20200615T12:24:38+02:30',
            DATABASE_HOST='c3po.droid.com'
        ),
        loader=dict(
            TASK_CLASS='test.datalabs.etl.test_load.Loader',
            EXECUTION_TIME='20200615T12:24:38+02:30',
            DATABASE_HOST='l337.droid.com'
        )
    )


@pytest.fixture
def event():
    current_env = os.environ.copy()

    os.environ['TASK_CLASS'] = 'test.datalabs.etl.test_awslambda.MockTask'
    os.environ['EXTRACTOR__TASK_CLASS'] = 'test.datalabs.etl.test_extract.Extractor'
    os.environ['EXTRACTOR__thing'] = 'True'
    os.environ['EXTRACTOR__DATABASE_HOST'] = 'r2d2.droid.com'
    os.environ['EXTRACTOR__DATABASE_SECRET'] = '{"username":"mrkitty", "password":"prettyboy59", "port":5432, ' \
                                             '"dbname":"mydatabase", "engine": "postgres"}'
    os.environ['EXTRACTOR__INCLUDE_NAMES'] = 'True'
    os.environ['TRANSFORMER__TASK_CLASS'] = 'test.datalabs.etl.test_transform.Transformer'
    os.environ['TRANSFORMER__DATABASE_HOST'] = 'c3po.droid.com'
    os.environ['LOADER__TASK_CLASS'] = 'test.datalabs.etl.test_load.Loader'
    os.environ['LOADER__DATABASE_HOST'] = 'l337.droid.com'

    yield dict(execution_time='20200615T12:24:38+02:30')

    os.environ.clear()
    os.environ.update(current_env)
