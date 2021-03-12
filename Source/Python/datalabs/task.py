""" Abstract task base class for use with AWS Lambda and other task-based systems. """
from abc import ABC, abstractmethod
import copy
import logging

import marshmallow

from   datalabs.access.database import Database
from   datalabs.access.parameter.system import ReferenceEnvironmentLoader

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class Task(ABC):
    PARAMETER_CLASS = None

    def __init__(self, parameters: dict):
        self._parameters = parameters

        if self.PARAMETER_CLASS:
            self._parameters = self._get_validated_parameters()

        LOGGER.debug('%s parameters: %s', self.__class__.__name__, self._parameters)

    @abstractmethod
    def run(self):
        pass

    def _get_validated_parameters(self):
        parameter_variables = {key.lower():value for key, value in self._parameters.items()}
        schema = self.PARAMETER_CLASS.SCHEMA

        return schema.load(parameter_variables)


class TaskException(BaseException):
    @property
    def message(self):
        return self.args[0]  # pylint: disable=unsubscriptable-object


class TaskWrapper(ABC):
    def __init__(self, task_class, parameters=None):
        self.task = None
        self.task_class = task_class
        self._parameters = parameters or {}
        self._task_parameters = None

        if not hasattr(self.task_class, 'run'):
            raise TypeError('Task class does not have a "run" method.')

    def run(self):
        self._setup_environment()

        self._task_parameters = self._get_task_parameters()

        self.task = self.task_class(self._task_parameters)

        try:
            self.task.run()

            response = self._handle_success()
        except TaskException as exception:
            response = self._handle_exception(exception)

        return response

    # pylint: disable=no-self-use
    def _setup_environment(self):
        secrets_loader = ReferenceEnvironmentLoader.from_environ()
        secrets_loader.load()

    def _get_task_parameters(self):
        return self._parameters

    @abstractmethod
    def _handle_success(self) -> (int, dict):
        pass

    @abstractmethod
    def _handle_exception(self, exception: Exception) -> (int, dict):
        pass


# pylint: disable=abstract-method
class DatabaseTaskMixin:
    @classmethod
    def _get_database(cls, database_class: Database, variables: dict):
        parameters = {}

        for key, value in variables.items():
            if key.startswith('DATABASE_'):
                parameters[key.lower()] = value.lower()

        return database_class.from_parameters(parameters, prefix='DATABASE_')


def add_schema(model_class):
    model_fields = [key for key, value in model_class.__dict__.items() if not key.startswith('_')]

    if '__dataclass_fields__' in model_class.__dict__:
        model_fields = [key for key, value in model_class.__dataclass_fields__.items() if not key.startswith('_')]

    class Schema(marshmallow.Schema):
        class Meta:
            # strict = True
            fields = copy.deepcopy(model_fields)

        @marshmallow.post_load
        #pylint: disable=unused-argument
        def make_model(self, data, **kwargs):
            model = None

            if '__dataclass_fields__' in model_class.__dict__:
                model = self._make_dataclass_model(data)
            else:
                model = self._make_class_model(data)

            return model

        def _make_dataclass_model(self, data):
            self._fill_dataclass_defaults(data)

            return model_class(**data)

        def _make_class_model(self, data):
            self._fill_class_defaults(data)
            model = model_class()

            for field in data:
                setattr(model, field, data[field])

            return model

        def _fill_dataclass_defaults(self, data):
            missing_fields = []

            for field in self.Meta.fields:
                dataclass_field = model_class.__dict__['__dataclass_fields__'][field]

                if field not in data and dataclass_field.default.__class__.__name__ != '_MISSING_TYPE':
                    data[field] = dataclass_field.default
                elif field not in data:
                    missing_fields.append(field)

            if len(missing_fields) > 0:
                raise TaskException(f'Missing parameters for {model_class.__name__} instance: {missing_fields}')

        def _fill_class_defaults(self, data):
            for field in self.Meta.fields:
                default = getattr(model_class, field)

                if field not in data:
                    data[field] = default

    model_class.SCHEMA = Schema()

    return model_class
