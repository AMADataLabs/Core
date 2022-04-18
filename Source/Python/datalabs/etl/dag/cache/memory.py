''' In-memory Task Data Cache implementation '''
from   datalabs.etl.dag.cache.base import TaskDataCache


class InMemoryTaskDataCache(TaskDataCache):
    FILES = {}

    def extract_data(self):
        return [self.FILES[file] for file in self._parameters["files"]]

    def load_data(self, output_data):
        for file, data in zip(self._parameters["files"], output_data):
            self.FILES[file]  = data

        return output_data
