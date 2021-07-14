""" Abstract task base class for use with AWS Lambda and other task-based systems. """
from abc import ABC, abstractmethod
import logging
import os

from   datalabs.access.database import Database
from   datalabs.access.parameter.etcd import EtcdEnvironmentLoader
from   datalabs.access.parameter.system import ReferenceEnvironmentLoader
from   datalabs.parameter import ParameterValidatorMixin
from   datalabs.plugin import import_plugin

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class Task(ParameterValidatorMixin, ABC):
    PARAMETER_CLASS = None

    def __init__(self, parameters: dict):
        self._parameters = parameters

        if self.PARAMETER_CLASS:
            self._parameters = self._get_validated_parameters(parameters)

        LOGGER.info('%s parameters: %s', self.__class__.__name__, self._parameters)

    @abstractmethod
    def run(self):
        pass


class TaskException(BaseException):
    @property
    def message(self):
        return self.args[0]  # pylint: disable=unsubscriptable-object


class TaskWrapper(ABC):
    def __init__(self, parameters=None):
        self.task = None
        self.task_class = None
        self._parameters = parameters or {}
        self._runtime_parameters = None
        self._task_parameters = None

        LOGGER.info('%s parameters: %s', self.__class__.__name__, self._parameters)

    def run(self):
        self._setup_environment()

        self.task_class = self._get_task_class()

        self._runtime_parameters = self._get_runtime_parameters(self._parameters)

        self._task_parameters = self._get_task_parameters()

        self._task_parameters = self._merge_parameters(self._task_parameters, self._runtime_parameters)

        self.task = self.task_class(self._task_parameters)

        try:
            self.task.run()

            response = self._handle_success()
        except TaskException as exception:
            response = self._handle_exception(exception)

        return response

    # pylint: disable=no-self-use
    def _setup_environment(self):
        etcd_loader = EtcdEnvironmentLoader.from_environ()
        if etcd_loader is not None:
            etcd_loader.load()

        secrets_loader = ReferenceEnvironmentLoader.from_environ()
        secrets_loader.load()

    def _get_task_class(self):
        task_resolver_class = self._get_task_resolver_class()

        task_class = task_resolver_class.get_task_class(self._parameters)

        if not hasattr(task_class, 'run'):
            raise TypeError('Task class does not have a "run" method.')

        return task_class

    # pylint: disable=unused-argument
    @classmethod
    def _get_runtime_parameters(cls, parameters):
        return {}

    def _get_task_parameters(self):
        return self._parameters

    @classmethod
    def _merge_parameters(cls, parameters, new_parameters):
        parameters.update(new_parameters)

        return parameters

    @abstractmethod
    def _handle_success(self) -> (int, dict):
        pass

    @abstractmethod
    def _handle_exception(self, exception: Exception) -> (int, dict):
        pass

    def _get_task_resolver_class(self):
        task_resolver_class_name = os.environ.get('TASK_RESOLVER_CLASS', 'datalabs.task.EnvironmentTaskResolver')
        task_resolver_class = import_plugin(task_resolver_class_name)

        if not hasattr(task_resolver_class, 'get_task_class'):
            raise TypeError(f'Task resolver {task_resolver_class_name} has no get_task_class method.')

        return task_resolver_class

class TaskResolver(ABC):
    @classmethod
    @abstractmethod
    def get_task_class(cls, parameters):
        pass


class EnvironmentTaskResolver(TaskResolver):
    # pylint: disable=unused-argument
    @classmethod
    def get_task_class(cls, parameters):
        task_class_name = os.environ['TASK_CLASS']

        return import_plugin(task_class_name)


# pylint: disable=abstract-method
class DatabaseTaskMixin:
    @classmethod
    def _get_database(cls, database_class: Database, variables: dict):
        parameters = {}

        for key, value in variables.items():
            if key.startswith('DATABASE_'):
                parameters[key.lower()] = value

        return database_class.from_parameters(parameters, prefix='DATABASE_')
