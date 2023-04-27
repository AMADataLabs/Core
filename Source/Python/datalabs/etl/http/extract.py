""" HTTP File Extractor """
from   dataclasses import dataclass
import itertools
import requests

from   datalabs.etl.extract import FileExtractorTask, IncludeNamesMixin
from   datalabs.parameter import add_schema


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class HTTPFileExtractorParameters:
    urls: str
    execution_time: str = None
    username: str = None
    password: str = None


class HTTPFileExtractorTask(IncludeNamesMixin, FileExtractorTask):
    PARAMETER_CLASS = HTTPFileExtractorParameters

    def _get_files(self):
        return self._parameters.urls.split(',')

    def _get_client(self):
        client = requests.Session()
        if self._parameters.username and self._parameters.password:
            client.auth = (self._parameters.username, self._parameters.password)
        return client

    def _resolve_wildcard(self, file):
        if '*' in file:
            raise NotImplementedError

        return [file]

    # pylint: disable=arguments-differ
    def _extract_file(self, file):
        text = self._client.get(file)

        return text.content


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class HTTPFileListExtractorParameters:
    execution_time: str = None
    username: str = None
    password: str = None


class HTTPFileListExtractorTask(HTTPFileExtractorTask):
    PARAMETER_CLASS = HTTPFileListExtractorParameters

    def _get_files(self):
        return list(itertools.chain.from_iterable(self._parse_url_lists(self._data)))

    def _get_client(self):
        client = super()._get_client()
        if self._parameters.username and self._parameters.password:
            client.auth = (self._parameters.username, self._parameters.password)
        return client

    @classmethod
    def _parse_url_lists(cls, data):
        for url_list in data:
            yield [url.decode().strip() for url in url_list.split(b'\n')]
