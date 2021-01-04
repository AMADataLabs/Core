""" HTTP File Extractor """
import requests

from   datalabs.etl.extract import FileExtractorTask


class HTTPFileExtractorTask(FileExtractorTask):
    def _extract(self):
        data = [self._extract_file(url) for url in self._parameters.variables['URLS'].split(',')]

        return data

    # pylint: disable=arguments-differ
    def _extract_file(self, url):
        with requests.Session() as http:
            text = http.get(url)

        return self._decode_data(text.content)

    @classmethod
    def _decode_data(cls, data):
        return data


class HTTPUnicodeTextFileExtractorTask(HTTPFileExtractorTask):
    @classmethod
    def _decode_data(cls, data):
        return data.decode('utf-8', errors='backslashreplace')
