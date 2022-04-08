''' Base ORM Loader Provider class and factory function '''
from  abc import ABC, abstractmethod

from  datalabs.plugin import import_plugin

class ORMLoaderProvider(ABC):
    @abstractmethod
    def get_primary_key(self, database, schema, table):
        pass

    @abstractmethod
    def get_database_columns(self, database, schema, table):
        pass

    @abstractmethod
    def get_current_row_hashes(self, database, schema, table, primary_key, columns):
        pass

    @classmethod
    @abstractmethod
    def generate_row_hashes(cls, data, primary_key, columns):
        pass


def get_provider(backend: str) -> ORMLoaderProvider:
    dialect = backend.split('+')[0]
    module_name = globals()['__name__']
    package_name = module_name.rsplit('.', 1)[0]
    provider_class_name = f'{package_name}.{dialect}.ORMLoaderProvider'

    return import_plugin(provider_class_name)()
