""" General ETL class """
class ETL:
    def __init__(self, configuration):
        self._configuration = configuration

    def run(self):
        data = self._extract()

        transformed_data = self._transform(data)

        self._load(transformed_data)

    def _extract(self):
        return self._configuration['EXTRACTOR'].extract()

    def _transform(self, data):
        return self._configuration['TRANSFORMER'].transform(data)

    def _load(self, data):
        self._configuration['LOADER'].load(data)
