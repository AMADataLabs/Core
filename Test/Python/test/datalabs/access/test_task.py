import pytest

import mock

import datalabs.access.task as apitask


class BadTask(apitask.APIEndpointTask):
    pass


class GoodTask(apitask.APIEndpointTask):
    def _run(self, session):
        GoodTask._run.called = True

GoodTask._run.called = False


def test_task_is_abstract():
    with pytest.raises(TypeError):
        BadTask(None)


def test_task_is_not_abstract():
    GoodTask(None)._run(None)


def test_task_runs_with_database(parameters):
    with mock.patch('datalabs.access.task.Database') as database:
        database.return_value.session = True
        task = GoodTask(parameters)
        task.run()

        assert database.call_count == 1
        assert database.return_value.session == True
        assert GoodTask._run.called == True


def test_api_endpoint_exceptions_have_status_and_message():
    exception = apitask.APIEndpointException('failed', -1)

    assert exception.status_code == -1
    assert exception.message == 'failed'


def test_default_api_endpoint_exception_status_code_is_400():
    exception = apitask.APIEndpointException('failed')

    assert exception.status_code == 400
    assert exception.message == 'failed'


def test_invalid_request_status_is_400():
    exception = apitask.InvalidRequest('failed')

    assert exception.status_code == 400
    assert exception.message == 'failed'


def test_resource_not_found_is_404():
    exception = apitask.ResourceNotFound('failed')

    assert exception.status_code == 404
    assert exception.message == 'failed'


@pytest.fixture
def parameters():
    return apitask.APIEndpointParameters(
        path=None,
        query=None,
        database=dict(name=None, backend=None, host=None, username=None, password=None)
    )
