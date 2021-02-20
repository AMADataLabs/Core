""" source: datalabs.awslambda """
import pytest

from datalabs.awslambda import TaskWrapper
from datalabs.task import Task, TaskException


def test_task_wrapper_is_abstract():
    with pytest.raises(TypeError):
        BadTaskWrapper(None)  # pylint: disable=abstract-class-instantiated


# pylint: disable=protected-access
def test_task_wrapper_is_not_abstract():
    wrapper = GoodTaskWrapper(MockTask)
    wrapper._get_task_parameters()
    wrapper._handle_exception(None)
    wrapper._handle_success()


def test_task_wrapper_succeeds_as_expected():
    wrapper = GoodTaskWrapper(MockTask, parameters=dict(fail=False))
    response = wrapper.run()

    assert response == 'succeeded'


def test_task_wrapper_fails_as_expected():
    wrapper = GoodTaskWrapper(MockTask, dict(fail=True))
    response = wrapper.run()

    assert response == 'failed'


# pylint: disable=abstract-method
class BadTaskWrapper(TaskWrapper):
    pass


class GoodTaskWrapper(TaskWrapper):
    def _get_task_parameters(self):
        return self._parameters

    def _handle_success(self) -> (int, dict):
        return 'succeeded'

    def _handle_exception(self, exception: Exception) -> (int, dict):
        return 'failed'


class MockTask(Task):
    def run(self):
        if self._parameters['fail']:
            raise MockTaskException('failed')


class MockTaskException(TaskException):
    pass
