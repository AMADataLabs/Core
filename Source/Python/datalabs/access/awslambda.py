import os

from   datalabs.access.task import APIEndpointTask, APIEndpointParameters, APIEndpointException
from   datalabs.awslambda import TaskWrapper


class APIEndpointTaskWrapper(TaskWrapper):
    def _get_task_parameters(self, event: dict):
        query_parameters = event.get('queryStringParameters') or dict()
        query_parameters.update(event.get('multiValueQueryStringParameters') or dict())

        return APIEndpointParameters(
            path=event.get('pathParameters') or dict(),
            query=query_parameters,
            database=dict(
                name=os.getenv('DATABASE_NAME'),
                backend=os.getenv('DATABASE_BACKEND'),
                host=os.getenv('DATABASE_HOST'),
                username=os.getenv('DATABASE_USERNAME'),
                password=os.getenv('DATABASE_PASSWORD')
            ),
        )

    def _handle_exception(self, exception: APIEndpointException) -> (int, dict):
        status_code = exception.status_code
        body = dict(message=exception.message)

        return status_code, body

    def _generate_response(self, task) -> (int, dict):
        return task.status_code, task.response_body
