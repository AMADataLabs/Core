""" source: datalabs.awslambda """
import logging
import os

import mock

from datalabs.awslambda import TaskWrapper
from datalabs.task import Task, TaskException

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


# pylint: disable=protected-access
def test_task_wrapper_is_not_abstract():
    os.environ['TASK_CLASS'] = 'test.datalabs.test_awslambda.GoodTask'

    wrapper = TaskWrapper(parameters=dict(fail=False))
    wrapper._get_task_parameters()
    wrapper._handle_exception(None)
    wrapper._handle_success()


def test_task_wrapper_succeeds_as_expected():
    os.environ['TASK_CLASS'] = 'test.datalabs.test_awslambda.GoodTask'

    with mock.patch('datalabs.access.parameter.aws.boto3'):
        with mock.patch('datalabs.access.secret.aws.boto3'):
            wrapper = TaskWrapper(parameters=dict(fail=False))
            response = wrapper.run()

    assert response == 'Success'


def test_task_wrapper_fails_as_expected():
    os.environ['TASK_CLASS'] = 'test.datalabs.test_awslambda.GoodTask'

    with mock.patch('datalabs.access.parameter.aws.boto3'):
        with mock.patch('datalabs.access.secret.aws.boto3'):
            wrapper = TaskWrapper(dict(fail=True))
            response = wrapper.run()

    assert response.startswith("Failed: ")


# pylint: disable=abstract-method
class BadTaskWrapper(TaskWrapper):
    pass


class GoodTask(Task):
    def run(self):
        if self._parameters['fail']:
            raise GoodTaskException('failed')


class BadTask(Task):
    pass


class GoodTaskException(TaskException):
    pass
