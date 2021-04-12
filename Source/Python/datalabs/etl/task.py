""" ETL Task base classes. """
from   dataclasses import dataclass
import logging

from   datalabs.access.environment import VariableTree
import datalabs.task as task
import datalabs.plugin as plugin

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@dataclass
class ETLParameters:
    extractor: dict
    transformer: dict
    loader: dict


class ETLTask(task.Task):
    def __init__(self, parameters):
        super().__init__(parameters)

        self._extractor = None
        self._transformer = None
        self._loader = None

    def run(self):
        try:
            self._extractor = self._instantiate_component(self._parameters.extractor)
        except Exception as exception:
            LOGGER.exception('Unable to instantiate ETL extractor sub-task')
            raise ETLException(f'Unable to instantiate ETL extractor sub-task: {exception}') from exception

        LOGGER.info('Extracting...')
        try:
            self._extractor.run()
        except Exception as exception:
            LOGGER.exception('Unable to run ETL extractor sub-task')
            raise ETLException(f'Unable to run ETL extractor sub-task: {exception}') from exception

        try:
            self._transformer = self._instantiate_component(self._parameters.transformer, self._extractor.data)
        except Exception as exception:
            LOGGER.exception('Unable to instantiate ETL transformer sub-task')
            raise ETLException(f'Unable to instantiate ETL transformer sub-task: {exception}') from exception

        LOGGER.info('Transforming...')
        try:
            self._transformer.run()
        except Exception as exception:
            LOGGER.exception('Unable to run ETL transformer sub-task')
            raise ETLException(f'Unable to run ETL transformer sub-task: {exception}') from exception

        try:
            self._loader = self._instantiate_component(self._parameters.loader, self._transformer.data)
        except Exception as exception:
            LOGGER.exception('Unable to instantiate ETL loader sub-task')
            raise ETLException(f'Unable to instantiate ETL loader sub-task: {exception}') from exception

        LOGGER.info('Loading...')
        try:
            self._loader.run()
        except Exception as exception:
            LOGGER.exception('Unable to run ETL loader sub-task')
            raise ETLException(f'Unable to run ETL loader sub-task: {exception}') from exception

    @classmethod
    def _instantiate_component(cls, parameters, data=None):
        parameters['data'] = data or {}
        task_class = parameters.pop('TASK_CLASS', None)

        if task_class is None:
            raise ETLException(f'...__TASK_CLASS parameter not specified in {parameters}')

        TaskPlugin = plugin.import_plugin(task_class)  # pylint: disable=invalid-name

        return TaskPlugin(parameters)


class ETLException(task.TaskException):
    pass


# pylint: disable=abstract-method
class ETLComponentTask(task.Task):
    def __init__(self, parameters):
        super().__init__(parameters)

        self._data = None

    @property
    def data(self):
        return self._data


class ETLTaskParametersGetterMixin(task.TaskWrapper):
    def _get_task_parameters(self):
        var_tree = VariableTree.generate()

        return ETLParameters(
            extractor=self._get_component_parameters(var_tree, "EXTRACTOR"),
            transformer=self._get_component_parameters(var_tree, "TRANSFORMER"),
            loader=self._get_component_parameters(var_tree, "LOADER")
        )

    @classmethod
    def _get_component_parameters(cls, var_tree, component):
        component_parameters = var_tree.get_branch_values([component]) or {}

        LOGGER.debug('Component parameters: %s', component_parameters)

        return component_parameters


class ETLTaskWrapper(ETLTaskParametersGetterMixin, task.TaskWrapper):
    def _get_task_parameters(self):
        task_parameters = super()._get_task_parameters()

        if self._parameters and hasattr(self._parameters, 'append'):
            task_parameters = self._add_component_environment_variables_from_parameters(
                task_parameters,
                self._parameters
            )

        return task_parameters

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
