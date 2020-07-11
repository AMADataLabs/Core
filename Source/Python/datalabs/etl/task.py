from dataclasses import dataclass

from datalabs.task import Task, TaskException


@dataclass
class ETLParameters:
    extractor: dict
    transformer: dict
    loader: dict
    database: dict


class ETLTask(Task):
    def __init__(self, parameters):
        super().__init__(parameters)

        self._extractor = None
        self._transformer = None
        self._loader = None

    def run(self):
        try:
            self._instantiate_plugins()
        except Exception as e:
            raise ETLException(f'Unable to instantiate ETL sub-tasks: {e}')

        self._logger.info('Extracting...')
        data = self._extract()

        self._logger.info('Transforming...')
        transformed_data = self._transform(data)

        self._logger.info('Loading...')
        self._load(transformed_data)

    def _instantiate_plugins(self, parameters):
        attributes = [self._extractor, self._transformer, self._loader]
        variable_base_names = ['EXTRACTOR', 'TRANSFORMER', 'LOADER']
        for attribute, variable_base_name in zip(attribute_names, variable_base_names):
            plugin_parameters = self._generate_parameters(parameters, variable_base_name)

            LOGGER.info('Instantiating ETL %s plugin', variable_base_name.lower())
            attribute = self._instantiate_plugin(plugin_parameters)

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

    def _instantiate_plugin(self, parameters):
        Plugin = plugin.import_plugin(parameters['CLASS'])  # pylint: disable=invalid-name

        return Plugin(parameters)

    def _extract(self):
        extractor = self._extractor(self._parameters.extractor)

        return extractor.extract()

    def _transform(self, data):
        transformer = self._transformer(self._parameters.transformer)

        return transformer.transform(data)

    def _load(self):
        loader = self._loader(self._parameters.loader)

        loader.load(transformed_data)

    def _instantiate_plugin(plugin_class, parameters):
        Plugin = plugin.import_plugin(plugin_class)  # pylint: disable=invalid-name

        return Plugin(parameters)


class ETLException(TaskException):
    pass

