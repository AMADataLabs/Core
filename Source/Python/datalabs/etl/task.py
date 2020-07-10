from abc import ABC, abstractmethod
from dataclasses import dataclass

from datalabs.access.credentials import Credentials
from datalabs.access.database import Configuration
from datalabs.access.orm import Database
from datalabs.etl.extract import Extractor
from datalabs.etl.transform import Transformer
from datalabs.etl.load import Loader
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

        self._session = None
        self._extractor = None
        self._transformer = None
        self._loader = None

    @property
    def session(self):
        return self._session

    def run(self):
        self._assert_components_configured()

        with self._get_database() as database:
            self._session - database.session

            self._logger.info('Extracting...')
            data = self._extract()

            self._logger.info('Transforming...')
            transformed_data = self._transform(data)

            self._logger.info('Loading...')
            self._load(transformed_data)

    def set_extractor(self, extractor):
        self._extractor = extractor

    def set_transformer(self, transformer):
        self._transformer = transformer

    def set_loader(self, loader):
        self._loader = loader

    def _get_database(self):
        config = Configuration(
            name=self._parameters.database['name'],
            backend=self._parameters.database['backend'],
            host=self._parameters.database['host']
        )
        credentials = Credentials(
            username=self._parameters.database['username'],
            password=self._parameters.database['password']
        )

        return Database(config, credentials)

    def _assert_components_configured(self):
        for component in ['extractor', 'transformer', 'loader']:
            self._assert_component_configured(component)

    def _extract(self):
        extractor = self._extractor(self, self._parameters.extractor)

        return extractor.extract()

    def _transform(self, data):
        transformer = self._transformer(self, self._parameters.transformer)

        return transformer.transform(data)

    def _load(self):
        loader = self._loader(self, self._parameters.loader)

        loader.load(transformed_data)

    def _assert_component_configured(self, component):
        if getattr(self, '_'+component) is None:
            raise ETLException('{component.capitalize()} was not configured.')


class ETLTaskComponent:
    def __init__(self, etl, parameters):
        self._etl = etl
        self._parameters = parameters


class ETLException(TaskException):
    pass
