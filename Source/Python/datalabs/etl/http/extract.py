""" HTTP File Extractor """
import requests

from   datalabs.etl.extract import FileExtractorTask, IncludeNamesMixin


class HTTPFileExtractorTask(IncludeNamesMixin, FileExtractorTask):
    def _get_files(self):
        return self._parameters['URLS'].split(',')

    def _get_client(self):
        return requests.Session()

    def _resolve_wildcard(self, file):
        if '*' in file:
            raise NotImplementedError

        return [file]

    # pylint: disable=arguments-differ
    def _extract_file(self, file):
        text = self._client.get(file)

        return text.content
