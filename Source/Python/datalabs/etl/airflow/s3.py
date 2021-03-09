''' Task Data Cache implementation for using S3 '''
from   datalabs.etl.airflow.task import TaskDataCache
from   datalabs.etl.s3.extract import S3UnicodeTextFileExtractorTask
from   datalabs.etl.s3.load import S3UnicodeTextFileLoaderTask


class S3TaskDataCache(TaskDataCache):
    def extract_data(self):
        ''' Pull cached data from files on S3, assuming is in CSV format.'''
        cache_parameters = self._parameters
        cache_extractor = S3UnicodeTextFileExtractorTask(cache_parameters)

        cache_extractor.run()

        return cache_extractor.data

    def load_data(self, output_data):
        self._parameters['data'] = output_data
        cache_parameters = self._parameters
        cache_loader = S3UnicodeTextFileLoaderTask(cache_parameters)

        cache_loader.run()

        return cache_loader.data
