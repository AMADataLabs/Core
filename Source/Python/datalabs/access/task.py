from   datalabs.task import Task


class APIEndpointTask(Task):
    def __init__(self, event):
        self._event = event


class APIException(Exception):
    def __init__(self, message, status_code=None):
        super().__init__(message)

        self._status_code = status_code or 400  # Invalid request


class InvalidRequest(Exception):
    pass


class ResourceNotFound(Exception):
    def __init__(self, message):
        super().__init__(message, 404)
