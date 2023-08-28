""" Abstract task base class for use with AWS Lambda and other task-based systems. """
from abc import ABCMeta, ABC, abstractmethod
import logging
import os

from   marshmallow.exceptions import ValidationError

from   datalabs.access.parameter.system import ReferenceEnvironmentLoader
from   datalabs.etl.dag.cache import CacheDirection, TaskDataCacheParameters, TaskDataCacheFactory
from   datalabs.parameter import ParameterValidatorMixin, ValidationException
from   datalabs.plugin import import_plugin

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class TaskMeta(ABCMeta):
    @property
    def name(cls):
        return f"{cls.__module__}.{cls.__name__}"


class Task(ParameterValidatorMixin, ABC, metaclass=TaskMeta):
    PARAMETER_CLASS = None

    def __init__(self, parameters: dict, data: "list<bytes>"=None):
        self._parameters = parameters
        self._data = data
        self._log_parameters(parameters)


        if self.PARAMETER_CLASS:
            self._parameters = self._get_validated_parameters(parameters)

    @abstractmethod
    def run(self) -> "list<bytes>":
        pass

    @classmethod
    def _log_parameters(cls, parameters):
        if hasattr(parameters, "__dataclass_fields__"):
            parameters = {key:getattr(parameters, key) for key in parameters.__dataclass_fields__.keys()}

        LOGGER.info('%s parameters: %s', cls.__name__, parameters)


class TaskFactory:
    @classmethod
    def create_task(cls, task_class: str, parameters: dict, data: bytes=None):
        task_class = import_plugin(task_class)

        if hasattr(task_class, "PARAMETER_CLASS"):
            parameters = cls._get_validated_parameters(task_class.PARAMETER_CLASS, parameters)

        if data is not None:
            parameters.data = data

        return task_class(parameters)

    @classmethod
    def _get_validated_parameters(cls, parameter_class, parameter_map: dict):
        parameter_map = {key.lower():value for key, value in parameter_map.items()}
        schema = parameter_class.SCHEMA  # pylint: disable=no-member
        parameters = None

        try:
            parameters = schema.load(parameter_map)
        except (ValidationException, ValidationError) as error:
            raise ValidationException(
                f'Parameter validation failed for {parameter_class.__name__} instance'
            ) from error

        return parameters


class TaskException(Exception):
    @property
    def message(self):
        return self.args[0]  # pylint: disable=unsubscriptable-object


class TaskWrapper(ABC):
    def __init__(self, parameters=None):
        self.task = None
        self.task_class = None
        self._parameters = parameters or {}
        self._task_parameters = None
        self._cache_parameters = None

        LOGGER.info('%s parameters: %s', self.__class__.__name__, self._parameters)

    def run(self):
        response = None

        try:
            self._setup_environment()

            self._task_parameters = self._get_task_parameters()

            self._cache_parameters = self._extract_cache_parameters(self._task_parameters)

            input_data = self._get_task_input_data()

            self.task_class = self._get_task_class()

            self.task = self.task_class(self._task_parameters, input_data)

            self._pre_run()

            output_data = self.task.run()

            self._put_task_output_data(output_data)

            response = self._handle_success()
        except Exception as exception:  # pylint: disable=broad-except
            LOGGER.exception('Unable to run task.')
            response = self._handle_exception(exception)

        return response

    # pylint: disable=no-self-use
    def _setup_environment(self):
        secrets_loader = ReferenceEnvironmentLoader.from_environ()
        secrets_loader.load()

    def _get_task_class(self):
        task_resolver_class = self._get_task_resolver_class()

        task_class = task_resolver_class.get_task_class(self._task_parameters)

        if not hasattr(task_class, 'run'):
            raise TypeError('Task class does not have a "run" method.')

        return task_class

    # pylint: disable=unused-argument
    def _pre_run(self):
        pass

    def _get_task_parameters(self):
        return os.environ

    @classmethod
    def _extract_cache_parameters(cls, task_parameters):
        return TaskDataCacheParameters.extract(task_parameters)

    def _get_task_input_data(self):
        data = []
        cache = TaskDataCacheFactory.create_cache(CacheDirection.INPUT, self._cache_parameters)

        if cache:
            data = cache.extract_data()

            if data:
                self._log_task_data_sizes(CacheDirection.INPUT, data)

        return data

    def _put_task_output_data(self, data):
        cache = TaskDataCacheFactory.create_cache(CacheDirection.OUTPUT, self._cache_parameters)

        if cache:
            if data:
                self._log_task_data_sizes(CacheDirection.OUTPUT, data)

            cache.load_data(data)

    @classmethod
    def _merge_parameters(cls, parameters, new_parameters):
        return {**parameters, **new_parameters}

    # pylint: disable=unused-argument
    def _handle_success(self) -> (int, dict):
        LOGGER.info("Task completed successfully.")

        return "Task completed successfully."

    # pylint: disable=unused-argument
    def _handle_exception(self, exception: Exception) -> (int, dict):
        LOGGER.exception("Task failed.")

        return "Task failed."

    def _get_task_resolver_class(self):
        task_resolver_class_name = os.environ.get('TASK_RESOLVER_CLASS', 'datalabs.task.EnvironmentTaskResolver')
        task_resolver_class = import_plugin(task_resolver_class_name)

        if not hasattr(task_resolver_class, 'get_task_class'):
            raise TypeError(f'Task resolver {task_resolver_class_name} has no get_task_class method.')

        return task_resolver_class

    @classmethod
    def _log_task_data_sizes(cls, direction, data):
        operation = "Received"

        if direction == CacheDirection.OUTPUT:
            operation = "Returning"

        for datum in data:
            LOGGER.debug('%s %d bytes.', operation, len(datum))

class TaskResolver(ABC):
    @classmethod
    @abstractmethod
    def get_task_class(cls, task_parameters):
        pass


class EnvironmentTaskResolver(TaskResolver):
    # pylint: disable=unused-argument
    @classmethod
    def get_task_class(cls, task_parameters):
        task_class_name = os.environ["TASK_CLASS"]

        return import_plugin(task_class_name)


class RuntimeTaskResolver(TaskResolver):
    @classmethod
    def get_task_class(cls, task_parameters):
        task_class_name = task_parameters["TASK_CLASS"]

        return import_plugin(task_class_name)
