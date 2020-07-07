from   abc import ABC, abstractmethod


class TaskWrapper:
    def __init__(self, task_class):
        self._task_class

    def run(self, event):
        status_code = 200
        body = None
        parameters = self._get_task_parameters(event)
        task = self._task_class(parameters)

        try:
            task.run()

            status_code, body = self._generate_response(task)
        except APIException as exception:
            status_code, body = self._handle_exception(exception)

        return {
            "statusCode": status_code,
            "body": json.dumps(response)
        }

    @abstractmethod
    def _get_task_parameters(self, event: dict):
        pass

    @abstractmethod
    def _handle_exception(self, exception: Exception) => (int, dict):
        pass

    @abstractmethod
    def _generate_response(self, task) => (int, dict):
        pass
