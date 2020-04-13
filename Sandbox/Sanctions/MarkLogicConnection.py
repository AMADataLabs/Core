import requests
from requests.auth import HTTPDigestAuth
import os
import json
from xml.dom import minidom
from pprint import pprint


class MarkLogicConnection(object):

    def __init__(self, url, username, password):
        self.auth = HTTPDigestAuth(username=username, password=password)
        self.url = url  # url takes the following form: "http://appd1454:8000/LATEST", "http://address:port/version"

    # returns a list of URIs resulting from a search query within some database/collection
    # empty query string will return all URIs in that collection
    def get_file_uris(self, database='PhysicianSanctions', collection='json_data', query=''):
        start = 1
        page_length = 100
        uris = []
        num_res = page_length

        # iterate through each page of results
        while num_res > 0:
            url = '{}/search?q={}&collection={}&start={}&pageLength={}&database={}'.format(self.url,
                                                                                           query,
                                                                                           collection,
                                                                                           str(start),
                                                                                           str(page_length),
                                                                                           database)
            # print(url)
            search = requests.get(url, auth=self.auth)
            #print(search.content)
            with open('pdf_search_results.xml', 'wb') as s:
               s.write(search.content)
            xmldoc = minidom.parse('pdf_search_results.xml')

            #xmldoc = minidom.parseString(search.content)

            res = xmldoc.getElementsByTagName('search:result')

            num_res = 0
            print('results len:', len(res))
            for r in res:
                num_res += 1
                uri = r.attributes['uri'].value
                uris.append(uri)

            start += page_length
        return uris

    def set_lic_nbr(self, uri, lic_nbr, database='PhysicianSanctions'):
        # step 1, download current metadata file
        url = '{}/documents?uri={}&database={}'.format(self.url, uri, database)
        response = requests.get(url=url, auth=self.auth)

        json_file = json.loads(response.content)

        # step 2, fill in license number
        json_file['sanction']['physician']['license'] = lic_nbr
        # print('Data to write:')
        # pprint(json_file)

        # step 3, upload edited file to update the document in MarkLogic
        resp = requests.put('{}/documents?uri={}&database={}'.format(self.url, uri, database),
                            auth=self.auth,
                            data=json.dumps(json_file))
        print(resp.status_code)
        return

    def set_me_nbr(self, uri, me_nbr, database='PhysicianSanctions'):
        # step 1, download current metadata file
        url = '{}/documents?uri={}&database={}'.format(self.url, uri, database)
        response = requests.get(url=url, auth=self.auth)

        json_file = json.loads(response.content)

        # step 2, fill in ME number
        json_file['sanction']['physician']['me'] = me_nbr
        json_file['app']['assignment']['me'] = me_nbr
        # print('Data to write:')
        # pprint(json_file)

        # step 3, upload edited file to update the document in MarkLogic
        resp = requests.put('{}/documents?uri={}&database={}'.format(self.url, uri, database),
                            auth=self.auth,
                            data=json.dumps(json_file))

        print(resp.status_code)
        return

    def get_file(self, uri, database='PhysicianSanctions'):
        url = '{}/documents?uri={}&database={}'.format(self.url, uri, database)

        response = requests.get(url=url, auth=self.auth)
        # should probably add more specific web response error handling
        if response.status_code != 200:
            print(response.status_code)
            response.raise_for_status()
            return None

        return response.content

    # downloads a file specified by URI to local environment
    def download_file(self, uri, database='PhysicianSanctions', save_dir=''):
        url = '{}/documents?uri={}&database={}'.format(self.url, uri, database)

        response = requests.get(url=url, auth=self.auth)
        if response.status_code != 200:
            print(response.status_code)
            print('oops')
            return

        # write the file
        # if not os.path.exists(save_dir):
        #     os.mkdir(save_dir)

        file = (save_dir + uri).replace('/', '\\').replace('\\\\', '\\')
        file_dir = file[:file.rindex('\\')]

        if not os.path.exists(file_dir):
            os.makedirs(file_dir)

        with open(file, 'wb+') as f:
            f.write(response.content)
        return
