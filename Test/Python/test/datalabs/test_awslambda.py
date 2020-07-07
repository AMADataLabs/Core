import pytest

from datalabs.awslambda import TaskWrapper
from datalabs.task import Task, TaskException


def test_task_wrapper_is_abstract():
    with pytest.raises(TypeError):
        BadTaskWrapper()


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



# def test_lambda_handler_returns_correct_success_response(event, context, expected_response_body):
#     with mock.patch('datalabs.access.cpt.api.cpt_descriptor_code.DescriptorEndpointTask.run') as run:
#         run.return_value = expected_response_body
#         response = lambda_handler(event, context)

#     assert 'statusCode' in response
#     assert response['statusCode'] == 200
#     assert 'body' in response
#     body = json.loads(response['body'])
#     assert body == expected_response_body


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
