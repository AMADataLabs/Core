""" source: datalabs.etl.task """
import datalabs.etl.task as etl


class ETLTaskWrapper(etl.ETLTaskWrapper):
    def __init__(self, task_class, parameters=None):
        super().__init__(task_class, parameters=parameters)

        self._exception=None
        self._data = None

    @property
    def exception(self):
        return self._exception

    @property
    def data(self):
        return self._data

    def _handle_exception(self, exception: etl.ETLException):
        self._exception = exception

    def _generate_response(self):
        self._data = dict(
            extractor=self._extractor.data,
            transformer=self._transformer.data,
            loader=self._loader.data
        )
