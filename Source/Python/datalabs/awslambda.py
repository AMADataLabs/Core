from   abc import ABC, abstractmethod
import json

from   datalabs.plugin import import_plugin
from   datalabs.task import Task, TaskException


class TaskWrapper(ABC):
    WRAPPER_CLASSES = dict()

    def __init__(self, task_class):
        self._task_class = task_class

    @classmethod
    def create(cls, task_class):
        task_class_name = '.'.join((task_class.__module__, task_class.__name__))
        wrapper_class_name = TaskWrapper.WRAPPER_CLASSES.get(task_class_name)

        if wrapper_class_name is None:
            raise ValueError(f'No wrapper class registered for task {task_class_name}.')

        wrapper_class = import_plugin(wrapper_class_name)

        return wrapper_class(task_class)

    @classmethod
    def register_task(cls, task_class_name):
        TaskWrapper.WRAPPER_CLASSES[task_class_name] = '.'.join((cls.__module__, cls.__name__))

    def run(self, event):
        status_code = 200
        body = None
        parameters = self._get_task_parameters(event)

        if self._task_class is None:
            raise KeyError('Task class is not set. Use/implement the wrap() method to set.')

        task = self._task_class(parameters)

        try:
            task.run()

            status_code, body = self._generate_response(task)
        except TaskException as exception:
            status_code, body = self._handle_exception(exception)

        return {
            "statusCode": status_code,
            "body": json.dumps(body)
        }

    @abstractmethod
    def _get_task_parameters(self, event: dict):
        pass

    @abstractmethod
    def _generate_response(self, task) -> (int, dict):
        pass

    @abstractmethod
    def _handle_exception(self, exception: Exception) -> (int, dict):
        pass
