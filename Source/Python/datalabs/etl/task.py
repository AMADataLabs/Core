""" ETL Task base classes. """
from   dataclasses import dataclass
import logging
from typing import Any

from   datalabs.access.environment import VariableTree
from   datalabs.task import Task, TaskException
import datalabs.plugin as plugin

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


@dataclass
class ETLParameters:
    extractor: dict
    transformer: dict
    loader: dict


class ETLTask(Task):
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
            raise ETLException(f'Unable to instantiate ETL extractor sub-task: {exception}')

        LOGGER.info('Extracting...')
        try:
            self._extractor.run()
        except Exception as exception:
            LOGGER.exception('Unable to run ETL extractor sub-task')
            raise ETLException(f'Unable to run ETL extractor sub-task: {exception}')

        try:
            self._transformer = self._instantiate_component(self._parameters.transformer, self._extractor.data)
        except Exception as exception:
            LOGGER.exception('Unable to instantiate ETL transformer sub-task')
            raise ETLException(f'Unable to instantiate ETL transformer sub-task: {exception}')

        LOGGER.info('Transforming...')
        try:
            self._transformer.run()
        except Exception as exception:
            LOGGER.error('Unable to run ETL transformer sub-task')
            raise ETLException(f'Unable to run ETL transformer sub-task: {exception}')

        try:
            self._loader = self._instantiate_component(self._parameters.loader, self._transformer.data)
        except Exception as exception:
            LOGGER.error('Unable to instantiate ETL loader sub-task')
            raise ETLException(f'Unable to instantiate ETL loader sub-task: {exception}')

        LOGGER.info('Loading...')
        try:
            self._loader.run()
        except Exception as exception:
            LOGGER.error('Unable to run ETL loader sub-task')
            raise ETLException(f'Unable to run ETL loader sub-task: {exception}')

    @classmethod
    def _instantiate_component(cls, parameters, data=None):
        parameters.data = data

        if 'CLASS' not in parameters.variables:
            raise ETLException(f'..._CLASS parameter not specified in {parameters.variables}')

        Plugin = plugin.import_plugin(parameters.variables['CLASS'])  # pylint: disable=invalid-name

        return Plugin(parameters)


class ETLException(TaskException):
    pass


# pylint: disable=abstract-method
class ETLComponentTask(Task):
    def __init__(self, parameters):
        super().__init__(parameters)

        self._data = None

    @property
    def data(self):
        return self._data


@dataclass
class ETLComponentParameters:
    database: dict
    variables: dict
    data: Any = None


class ETLTaskWrapper(TaskWrapper):
    def _get_task_parameters(self, event: dict):
        var_tree = VariableTree.generate()

        return ETLParameters(
            extractor=self._get_component_parameters(var_tree, "EXTRACTOR"),
            transformer=self._get_component_parameters(var_tree, "TRANSFORMER"),
            loader=self._get_component_parameters(var_tree, "LOADER")
        )

    def _handle_exception(self, exception: ETLException) -> (int, dict):
        LOGGER.error('Handling ETL task exception: %s', exception)

    def _generate_response(self, task) -> (int, dict):
        LOGGER.info('ETL task has finished')
        pass

    @classmethod
    def _get_component_parameters(cls, var_tree, component):
        component_variables = var_tree.get_branch_values([component])
        database_variables = var_tree.get_branch_values([component, 'DATABASE'])

        LOGGER.debug('Component variables: %s', component_variables)
        LOGGER.debug('Database variables: %s', database_variables)

        return ETLComponentParameters(database=database_parameters, variables=component_variables)
