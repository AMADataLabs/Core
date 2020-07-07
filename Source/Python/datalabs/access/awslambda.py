import os

from   datalabs.access.task import APIEndpointTask, APIEndpointParameters, APIEndpointException


class APIEndpointTaskWrapper:
    def __init__(self):
        super().__init__(APIEndpointTask)

    def _get_task_parameters(self, event: dict):
        query_parameters = event.get('queryStringParameters', dict())
        query_parameters.update(event.get('multiValueQueryStringParameters', dict()))

        return APIEndpointParameters(
            path=event.get('pathParameters', dict()),
            query=query_parameters,
            database=dict(
                name=os.getenv('DATABASE_NAME'),
                host=os.getenv('DATABASE_HOST'),
                backend=os.getenv('DATABASE_BACKEND'),
                username=os.getenv('DATABASE_USERNAME'),
                password=os.getenv('DATABASE_PASSWORD')
            ),
        )

    def _handle_exception(self, exception: Exception) => (int, dict):
        status_code = exception.status_code
        response = dict(message=str(exception))

        return status_code, response

    def _generate_response(self, task) => (int, dict):
        return task.status_code, task.response_body
