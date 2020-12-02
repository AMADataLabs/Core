""" source: datalabs.etl.task """
from   datalabs.etl.task import ETLTaskWrapper


class ETLTaskWrapper(ETLTaskWrapper):
    def __init__(self, task_class, parameters=None):
        super().__init__(task_class, parameters=parameters)

        self._exception
        self._data = None

    @propery
    def exception(self):
        return self._exception

    @property
    def data(self):
        return self._data

    def _handle_exception(self, exception: ETLException):
        self._exception = exception

    def _generate_response(self):
        self._data = dict(
            extractor=self._extractor.data,
            transformer=self._transformer.data,
            loader=self._loader.data
        )
