""" source: datalabs.awslambda """
import mock
import os
import pytest

from datalabs.awslambda import TaskWrapper
from datalabs.task import Task, TaskException


def test_task_wrapper_is_abstract():
    os.environ['TASK_CLASS'] = 'test.datalabs.test_awslambda.BadTask'

    task_wrapper = BadTaskWrapper(parameters=dict(fail=False))  # pylint: disable=abstract-class-instantiated

    with pytest.raises(TypeError):
        task_wrapper.run()


# pylint: disable=protected-access
def test_task_wrapper_is_not_abstract():
    os.environ['TASK_CLASS'] = 'test.datalabs.test_awslambda.GoodTask'

    wrapper = GoodTaskWrapper(parameters=dict(fail=False))
    wrapper._get_task_parameters()
    wrapper._handle_exception(None)
    wrapper._handle_success()


def test_task_wrapper_succeeds_as_expected():
    os.environ['TASK_CLASS'] = 'test.datalabs.test_awslambda.GoodTask'

    with mock.patch('datalabs.access.parameter.aws.boto3'):
        with mock.patch('datalabs.access.secret.aws.boto3'):
            wrapper = GoodTaskWrapper(parameters=dict(fail=False))
            response = wrapper.run()

    assert response == 'succeeded'


def test_task_wrapper_fails_as_expected():
    os.environ['TASK_CLASS'] = 'test.datalabs.test_awslambda.GoodTask'

    with mock.patch('datalabs.access.parameter.aws.boto3'):
        with mock.patch('datalabs.access.secret.aws.boto3'):
            wrapper = GoodTaskWrapper(dict(fail=True))
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


class GoodTask(Task):
    def run(self):
        if self._parameters['fail']:
            raise GoodTaskException('failed')


class BadTask(Task):
    pass


class GoodTaskException(TaskException):
    pass
