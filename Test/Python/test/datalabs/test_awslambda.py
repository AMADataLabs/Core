""" REPLACE WITH DOCSTRING """
import pytest

from datalabs.awslambda import TaskWrapper
from datalabs.task import Task, TaskException


def test_task_wrapper_is_abstract():
    with pytest.raises(TypeError):
        BadTaskWrapper(None)


def test_task_wrapper_is_not_abstract():
    wrapper = GoodTaskWrapper(MockTask)
    wrapper._get_task_parameters(None)
    wrapper._handle_exception(None)
    wrapper._generate_response(None)


def test_task_wrapper_succeeds_as_expected():
    wrapper = GoodTaskWrapper(MockTask)
    response = wrapper.run(dict(fail=False))

    assert response['statusCode'] == 200
    assert response['body'] == '"succeeded"'


def test_task_wrapper_succeeds_as_expected():
    wrapper = GoodTaskWrapper(MockTask)
    response = wrapper.run(dict(fail=True))

    assert response['statusCode'] == 400
    assert response['body'] == '"failed"'


class BadTaskWrapper(TaskWrapper):
    pass


class GoodTaskWrapper(TaskWrapper):
    def _get_task_parameters(self, event: dict):
        return event

    def _generate_response(self, task) -> (int, dict):
        return 200, 'succeeded'

    def _handle_exception(self, exception: Exception) -> (int, dict):
        return 400, 'failed'


class MockTask(Task):
    def run(self):
        if self._parameters['fail']:
            raise MockTaskException('failed')


class MockTaskException(TaskException):
    pass
