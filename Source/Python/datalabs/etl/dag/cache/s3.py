''' Task Data Cache implementation for using S3 '''
from   datalabs.cache.base import TaskDataCache
from   datalabs.etl.s3.extract import S3FileExtractorTask
from   datalabs.etl.s3.load import S3FileLoaderTask


class S3TaskDataCache(TaskDataCache):
    def extract_data(self):
        ''' Pull cached data from files on S3, assuming is in CSV format.'''
        cache_extractor = S3FileExtractorTask(self._parameters)

        return cache_extractor.run()

    def load_data(self, output_data):
        cache_loader = S3FileLoaderTask(self._parameters, output_data)

        cache_loader.run()
