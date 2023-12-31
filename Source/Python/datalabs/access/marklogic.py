"""Class for accessing marklogic"""
from   dataclasses import dataclass
import os
from   xml.dom import minidom

import requests
from   requests.auth import HTTPDigestAuth

from   datalabs.access.database import Database
from   datalabs.parameter import add_schema


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class MarkLogicParameters:
    host: str
    port: str
    username: str
    password: str
    protocol: str="http"
    version: str="LATEST"


class MarkLogic(Database):
    PARAMETER_CLASS = MarkLogicParameters

    def connect(self):
        self._connection = requests.Session()
        self._connection.auth = HTTPDigestAuth(self._parameters.username, self._parameters.password)

        # test connection
        response = self._connection.get(self.connection_string.replace('/LATEST', ''))
        response.raise_for_status()

    def get_file_uris(self, database='PhysicianSanctions', collection='json_data', query=''):
        """
        returns a list of URIs resulting from a search query within some database/collection
        empty query string will return all URIs in that collection
        can be used to query json_data or pdf_data collections
        """
        start = 1
        page_length = 100
        uris = []
        page_results = page_length

        # iterate through each page of results, building a list of URIs
        while page_results == page_length:  # if the results page for the previous search is full, search next page
            page_result = self._get_page_search_result(query, collection, start, page_length, database)
            page_result_uris = self._get_search_result_uris(page_result)
            uris.extend(page_result_uris)
            page_results = len(page_result_uris)
            start += page_length
        return uris

    # downloads a file specified by URI to local environment
    def download_file(self, uri, database='PhysicianSanctions', save_dir=''):
        data = self.get_file(uri=uri, database=database)
        self.write_file(data, file_name=uri, save_dir=save_dir)

    def get_file(self, uri, database='PhysicianSanctions'):
        url = f'{self.connection_string}/documents?uri={uri}&database={database}'

        response = self._connection.get(url=url)
        response.raise_for_status()
        return response.content

    @classmethod
    def write_file(cls, data, file_name, save_dir=''):
        """ File names by default are the URI of the file, which themselves often contain relative paths. """
        file_path = (save_dir + file_name).replace('/', '\\').replace('\\\\', '\\')
        file_dir = file_path[:file_path.rindex('\\') if '\\' in file_path else '']

        if not os.path.exists(file_dir):
            os.makedirs(file_dir)

        with open(file_path, 'wb+') as file:
            file.write(data)

    def _generate_connection_string(self):
        protocol = self._parameters.protocol or "http"
        version = self._parameters.version or "LATEST"

        return f"{protocol}://{self._parameters.host}:{self._parameters.port}/{version}"

    # pylint: disable=too-many-arguments
    def _get_page_search_result(self, query, collection, start, page_length, database):
        url = f'{self.connection_string}/search?q={query}&collection={collection}&start={start}&' \
              f'pageLength={page_length}&database={database}'
        search = self._connection.get(url)
        search.raise_for_status()
        return search

    def _get_search_result_uris(self, response):
        uris = []

        results = self._get_results_from_search(response)
        for result in results:
            uri = result.attributes['uri'].value
            uris.append(uri)
        return uris

    @classmethod
    def _get_results_from_search(cls, response):
        xml_doc = minidom.parse(response.content)
        results = xml_doc.getElementsByTagName('search:result')
        return results
