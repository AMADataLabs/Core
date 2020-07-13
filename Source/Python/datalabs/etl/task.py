from   dataclasses import dataclass
import logging

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
        LOGGER.info('Extracting...')
        try:
            self._extractor = self._instantiate_plugin(self._parameters.extractor)

            self._extractor.run()
        except Exception as e:
            raise ETLException(f'Unable to instantiate ETL extractor sub-task: {e}')

        LOGGER.info('Transforming...')
        try:
            self._transformer = self._instantiate_plugin(self._parameters.transformer, self._extractor.data)

            self._transformer.run()
        except Exception as e:
            raise ETLException(f'Unable to instantiate ETL transformer sub-task: {e}')

        LOGGER.info('Loading...')
        try:
            self._loader = self._instantiate_plugin(self._parameters.loader, self._transformer.data)

            self._loader.run()
        except Exception as e:
            raise ETLException(f'Unable to instantiate ETL loader sub-task: {e}')

    def _instantiate_plugin(self, parameters, data=None):
        parameters['data'] = data

        if 'CLASS' not in parameters:
            raise ETLException('..._CLASS parameter not specified in %s', parameters)

        Plugin = plugin.import_plugin(parameters['CLASS'])  # pylint: disable=invalid-name

        return Plugin(parameters)

    @classmethod
    def _generate_parameters(cls, variables, variable_base_name):
        LOGGER.debug('Variables: %s', variables)
        LOGGER.debug('Variable Base Name: %s', variable_base_name)
        parameters = {
            name[len(variable_base_name)+1:]:value
            for name, value in variables.items()
            if name.startswith(variable_base_name + '_')
        }

        if not parameters:
            LOGGER.debug('parameters: %s', parameters)
            LOGGER.warn(f'No parameters for "{variable_base_name}" in {variables}')

        return parameters


class ETLComponentTask(Task):
    def __init__(self, parameters):
        super().__init__(parameters)

        self._data = None

    @property
    def data(self):
        return self._data
    

class ETLException(TaskException):
    pass

