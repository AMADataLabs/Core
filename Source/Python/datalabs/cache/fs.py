''' Task Data Cache implementation for using the local file system '''
from   datalabs.cache.base import TaskDataCache
from   datalabs.etl.fs.extract import LocalFileExtractorTask
from   datalabs.etl.fs.load import LocalFileLoaderTask


class LocalTaskDataCache(TaskDataCache):
    def extract_data(self):
        ''' Pull cached data from files on the local file system.'''
        cache_extractor = LocalFileExtractorTask(self._parameters)

        return cache_extractor.run()

    def load_data(self, output_data):
        cache_loader = LocalFileLoaderTask(self._parameters, output_data)

        cache_loader.run()
