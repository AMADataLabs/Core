""" API endpoint-specific Lambda function Task wrapper. """
import datalabs.access.task.api as api
from   datalabs.awslambda import TaskWrapper


class APIEndpointTaskWrapper(
    api.APIEndpointParametersGetterMixin, api.APIEndpointResponseHandlerMixin, TaskWrapper
):
    def _get_task_parameters(self):
        self._parameters['query'] = self._parameters.get('queryStringParameters') or dict()
        self._parameters['query'].update(self._parameters.get('multiValueQueryStringParameters') or dict())
        self._parameters['path'] = self._parameters.get('pathParameters') or dict()

        return super()._get_task_parameters()
