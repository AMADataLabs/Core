import requests
from requests.auth import HTTPDigestAuth
import os
import json
from xml.dom import minidom

from datalabs.access.datastore import Datastore
from datalabs.access.credentials import Credentials


class MarkLogic(Datastore):
    def __init(self, credentials: Credentials = None, url=None):
        super().__init__(credentials, key='MARKLOGIC')
        self.url = url  # url takes the following form: "http://address:port/version"
        self.auth = HTTPDigestAuth(credentials.username, credentials.password)

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
        num_res = page_length

        # iterate through each page of results
        while num_res > 0:
            url = f'{self.url}/search?q={query}&collection={collection}&start={start}&' \
                  f'pageLength={page_length}&database={database}'
            search = self._connection.get(url, auth=self.auth)
            xmldoc = minidom.parse(search.content)
            res = xmldoc.getElementsByTagName('search:result')

            num_res = 0
            for r in res:
                num_res += 1
                uri = r.attributes['uri'].value
                uris.append(uri)

            start += page_length
        return uris

    def get_file(self, uri, database='PhysicianSanctions'):
        url = '{}/documents?uri={}&database={}'.format(self.url, uri, database)

        response = self._connection.get(url=url, auth=self.auth)
        response.raise_for_status()

        return response.content

    # downloads a file specified by URI to local environment
    def download_file(self, uri, database='PhysicianSanctions', save_dir=''):
        url = '{}/documents?uri={}&database={}'.format(self.url, uri, database)

        response = requests.get(url=url, auth=self.auth)
        response.raise_for_status()

        file = (save_dir + uri).replace('/', '\\').replace('\\\\', '\\')
        file_dir = file[:file.rindex('\\')]

        if not os.path.exists(file_dir):
            os.makedirs(file_dir)

        with open(file, 'wb+') as f:
            f.write(response.content)
