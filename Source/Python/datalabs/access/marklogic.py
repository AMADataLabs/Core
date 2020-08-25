import requests
from requests.auth import HTTPDigestAuth
import os
import json
from xml.dom import minidom

from datalabs.access.datastore import Datastore
from datalabs.access.credentials import Credentials


class MarkLogic(Datastore):
    def __init(self, credentials: Credentials = None, url=None):
        super().__init__(credentials, key='MARKLOGIC_TEST')
        self.url = url  # url takes the following form: "http://address:port/version"
        self.auth = HTTPDigestAuth(self._credentials.username, self._credentials.password)
        self._connection = None
        self.connect()

    def connect(self):
        self._connection = requests.Session()
        self._connection.auth = self.auth
        # test connection
        response = self._connection.get(self.url.replace('/LATEST', ''))
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
        url = '{}/documents?uri={}&database={}'.format(self.url, uri, database)

        response = self._connection.get(url=url, auth=self.auth)
        response.raise_for_status()
        return response.content

    @classmethod
    def write_file(cls, data, file_name, save_dir=''):
        """ File names by default are the URI of the file, which themselves often contain relative paths. """
        file = (save_dir + file_name).replace('/', '\\').replace('\\\\', '\\')
        file_dir = file[:file.rindex('\\') if '\\' in file else '']

        if not os.path.exists(file_dir):
            os.makedirs(file_dir)

        with open(file, 'wb+') as f:
            f.write(data)

    def _get_page_search_result(self, query, collection, start, page_length, database):
        url = f'{self.url}/search?q={query}&collection={collection}&start={start}&' \
              f'pageLength={page_length}&database={database}'
        search = self._connection.get(url, auth=self.auth)
        search.raise_for_status()
        return search

    def _get_search_result_uris(self, response):
        uris = []

        results = self._get_results_from_search(response)
        for r in results:
            uri = r.attributes['uri'].value
            uris.append(uri)
        return uris

    @classmethod
    def _get_results_from_search(cls, response):
        xml_doc = minidom.parse(response.content)
        results = xml_doc.getElementsByTagName('search:result')
        return results
