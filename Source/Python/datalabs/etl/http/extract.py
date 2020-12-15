""" HTTP File Extractor """
import requests

from   datalabs.etl.extract import FileExtractorTask


class HTTPFileExtractorTask(FileExtractorTask):
    def _extract(self):

        with requests.Session() as http:
            text = [http.get(url) for url in self.parameters.variables['URLS'].split(',')]

        return [self._decode_data(data) for data in text]

    @classmethod
    def _decode_data(cls, data):
        return data


class HTTPUnicodeTextFileExtractorTask(HTTPFileExtractorTask):
    @classmethod
    def _decode_data(cls, data):
        return data.decode('utf-8', errors='backslashreplace')
