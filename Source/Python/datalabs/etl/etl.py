""" General ETL class """
import logging

class ETL:
    def __init__(self, configuration):
        self._configuration = configuration
        self._logger = logging.getLogger(ETL.__name__)
        self._logger.setLevel(logging.INFO)

    def run(self):
        self._logger.info('Extracting...')
        data = self._extract()

        self._logger.info('Transforming...')
        transformed_data = self._transform(data)

        self._logger.info('Loading...')
        self._load(transformed_data)

    def _extract(self):
        return self._configuration['EXTRACTOR'].extract()

    def _transform(self, data):
        return self._configuration['TRANSFORMER'].transform(data)

    def _load(self, data):
        self._configuration['LOADER'].load(data)
