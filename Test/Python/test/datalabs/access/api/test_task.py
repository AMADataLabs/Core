""" source: datalabs.access.api.task """
import pytest

import datalabs.access.api.task as api


# pylint: disable=abstract-method
class BadTask(api.APIEndpointTask):
    pass


# pylint: disable=protected-access
class GoodTask(api.APIEndpointTask):
    # pylint: disable=unused-argument
    def run(self):
        GoodTask.run.called = True


GoodTask.run.called = False  # pylint: disable=protected-access


def test_task_is_abstract():
    with pytest.raises(TypeError):
        BadTask(None)  # pylint: disable=abstract-class-instantiated


# pylint: disable=protected-access
def test_task_is_not_abstract():
    GoodTask(None).run()


def test_api_endpoint_exceptions_have_status_and_message():
    exception = api.APIEndpointException('failed', -1)

    assert exception.status_code == -1
    assert exception.message == 'failed'


def test_default_api_endpoint_exception_status_code_is_400():
    exception = api.APIEndpointException('failed')

    assert exception.status_code == 400
    assert exception.message == 'failed'


def test_invalid_request_status_is_400():
    exception = api.InvalidRequest('failed')

    assert exception.status_code == 400
    assert exception.message == 'failed'


def test_resource_not_found_is_404():
    exception = api.ResourceNotFound('failed')

    assert exception.status_code == 404
    assert exception.message == 'failed'# pylint: disable=redefined-outer-name, protected-access