import requests
from requests.auth import HTTPDigestAuth
import os
import json
from xml.dom import minidom
from pprint import pprint


class MarkLogicConnection(object):

    def __init__(self, username, password, url=None, server='prod'):
        self.auth = HTTPDigestAuth(username=username, password=password)
        self.url = url  # url takes the following form: "http://address:port/version"

        if url is None:
            # server URLs
            prod = 'http://appp1462:8000/LATEST'
            test = 'http://appt1456:8000/LATEST'
            dev  = 'http://appd1454:8000/LATEST'

            # server aliases linked to URLs
            servers = {
                ('prod', 'production'): prod,
                ('test'):               test,
                ('dev', 'development'): dev}

            for aliases in servers:
                if server in aliases:
                    self.url = servers[aliases]

        if self.url is None:
            raise ValueError("server '{}' not found in server aliases.".format(server))

        # test connection
        response = requests.get(self.url.replace('/LATEST', ''), auth=self.auth)
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
            search = requests.get(url, auth=self.auth)
            xmldoc = minidom.parse(search.content)
            res = xmldoc.getElementsByTagName('search:result')

            num_res = 0
            for r in res:
                num_res += 1
                uri = r.attributes['uri'].value
                uris.append(uri)

            start += page_length
        return uris

    def set_lic_nbr(self, uri, lic_nbr, json_file=None, database='PhysicianSanctions'):
        # step 1, download current metadata file
        url = f'{self.url}/documents?uri={uri}&database={database}'

        # if json_file can be passed from a previous download, we don't need to re-download the file
        if json_file is None:
            # Download file
            response = requests.get(url=url,
                                    auth=self.auth)
            json_file = json.loads(response.content)

        # Fill in license number
        json_file['sanction']['physician']['license'] = lic_nbr

        # Upload edited file to update the document in MarkLogic
        response = requests.put(url,
                                auth=self.auth,
                                data=json.dumps(json_file))
        response.raise_for_status()
        return

    def set_me_nbr(self, uri, me_nbr, json_file=None, database='PhysicianSanctions'):
        url = f'{self.url}/documents?uri={uri}&database={database}'

        # if json_file can be passed from a previous download, we don't need to re-download the file
        if json_file is None:
            # Download file
            response = requests.get(url=url,
                                    auth=self.auth)
            json_file = json.loads(response.content)

        # Fill ME number
        json_file['sanction']['physician']['me'] = me_nbr
        json_file['app']['assignment']['me'] = me_nbr

        # Upload edited file to update the document in MarkLogic
        response = requests.put(url=url,
                                auth=self.auth,
                                data=json.dumps(json_file))
        response.raise_for_status()

    def get_file(self, uri, database='PhysicianSanctions'):
        url = '{}/documents?uri={}&database={}'.format(self.url, uri, database)

        response = requests.get(url=url, auth=self.auth)
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
