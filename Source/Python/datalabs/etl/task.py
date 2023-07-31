""" ETL Task base classes. """
from   collections import namedtuple
from   dataclasses import dataclass
from   datetime import datetime
import logging

from   dateutil.parser import isoparse

from   datalabs.access.environment import VariableTree
from   datalabs.task import Task, TaskException, TaskWrapper
from   datalabs.parameter import add_schema
from   datalabs.plugin import import_plugin

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


ETLAggregate = namedtuple("ETLAggregate", "extractor transformer loader")  # pylint: disable=too-many-function-args


@add_schema
@dataclass
class ETLParameters:
    extractor: dict
    transformer: dict
    loader: dict


class ETLTask(Task):
    PARAMETER_CLASS = ETLParameters

    def __init__(self, parameters: dict, data: "list<bytes>"=None):
        super().__init__(parameters, data)

        self._subtasks = None
        self._output = None

    def run(self):
        try:
            extractor = self._instantiate_component(self._parameters.extractor)
        except Exception as exception:
            LOGGER.exception('Unable to instantiate ETL extractor sub-task')
            raise ETLException(f'Unable to instantiate ETL extractor sub-task: {exception}') from exception

        LOGGER.info('Extracting...')
        try:
            extractor_output = extractor.run()
        except Exception as exception:
            LOGGER.exception('Unable to run ETL extractor sub-task')
            raise ETLException(f'Unable to run ETL extractor sub-task: {exception}') from exception

        try:
            transformer = self._instantiate_component(self._parameters.transformer, extractor_output)
        except Exception as exception:
            LOGGER.exception('Unable to instantiate ETL transformer sub-task')
            raise ETLException(f'Unable to instantiate ETL transformer sub-task: {exception}') from exception

        LOGGER.info('Transforming...')
        try:
            transformer_output = transformer.run()
        except Exception as exception:
            LOGGER.exception('Unable to run ETL transformer sub-task')
            raise ETLException(f'Unable to run ETL transformer sub-task: {exception}') from exception

        try:
            loader = self._instantiate_component(self._parameters.loader, transformer_output)
        except Exception as exception:
            LOGGER.exception('Unable to instantiate ETL loader sub-task')
            raise ETLException(f'Unable to instantiate ETL loader sub-task: {exception}') from exception

        LOGGER.info('Loading...')
        try:
            loader_output = loader.run()
        except Exception as exception:
            LOGGER.exception('Unable to run ETL loader sub-task')
            raise ETLException(f'Unable to run ETL loader sub-task: {exception}') from exception

        self._subtasks = ETLAggregate(extractor, transformer, loader)
        self._output = ETLAggregate(extractor_output, transformer_output, loader_output)

        return []

    @classmethod
    def _instantiate_component(cls, parameters, data=None):
        task_class = parameters.pop('TASK_CLASS', None)

        if task_class is None:
            raise ETLException(f'...__TASK_CLASS parameter not specified in {parameters}')

        TaskPlugin = import_plugin(task_class)  # pylint: disable=invalid-name

        return TaskPlugin(parameters, data)


class ETLException(TaskException):
    pass


class DummyTask(Task):
    def run(self):
        LOGGER.info("I'm a dummy!")
        return []


class ETLTaskParametersGetterMixin(TaskWrapper):
    def _get_task_parameters(self):
        var_tree = VariableTree.from_environment()

        return dict(
            extractor=self._get_component_parameters(var_tree, "EXTRACTOR"),
            transformer=self._get_component_parameters(var_tree, "TRANSFORMER"),
            loader=self._get_component_parameters(var_tree, "LOADER")
        )

    @classmethod
    def _get_component_parameters(cls, var_tree, component):
        component_parameters = var_tree.get_branch_values([component]) or {}

        LOGGER.debug('Component parameters: %s', component_parameters)

        return component_parameters


class ETLTaskWrapper(ETLTaskParametersGetterMixin, TaskWrapper):
    def _get_task_parameters(self):
        task_parameters = super()._get_task_parameters()

        if self._parameters and hasattr(self._parameters, 'append'):
            task_parameters = self._add_component_environment_variables_from_parameters(
                task_parameters,
                self._parameters
            )

        return task_parameters

    @classmethod
    def _merge_parameters(cls, parameters, new_parameters):
        return parameters

    def _handle_exception(self, exception: ETLException):
        LOGGER.exception('Handling ETL task exception: %s', exception)

    def _handle_success(self):
        LOGGER.info('ETL task has finished')

    @classmethod
    def _add_component_environment_variables_from_parameters(cls, task_parameters, parameters):
        base_task_parameters = {key:value for key, value in (parameter.split('=') for parameter in parameters[1:])}  # pylint: disable=unnecessary-comprehension
        component_variables = [
            task_parameters.extractor,
            task_parameters.transformer,
            task_parameters.loader
        ]

        for variables in component_variables:
            base_component_variables = base_task_parameters.copy()
            base_component_variables.update(variables)
            variables.clear()
            variables.update(base_component_variables)

        return task_parameters


class ExecutionTimeMixin:
    @property
    def execution_time(self):
        timestamp = datetime.utcnow().isoformat()

        if hasattr(self._parameters, 'execution_time') and self._parameters.execution_time:
            timestamp = self._parameters.execution_time
        elif hasattr(self._parameters, 'get'):
            timestamp = self._parameters.get('EXECUTION_TIME', timestamp)

        return isoparse(timestamp)
