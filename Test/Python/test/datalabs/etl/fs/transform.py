""" source: datalabs.etl.fs.transform """
from datalabs.task import Task


class FilenameStripperTransformerTask(Task):
    def run(self):
        return [datum for _, datum in self._data]
