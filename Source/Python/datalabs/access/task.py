from   datalabs.task import Task


class APIEndpointTask(Task):
    def __init__(self, event):
        self._event = event