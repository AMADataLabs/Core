import requests
import json
from datalabs.access import marklogic


class MarkLogic(marklogic.MarkLogic):
    def __init__(self, url=None, server=None):
        super().__init__()
        if url is None:
            # server URLs
            prod = 'http://appp1462:8000/LATEST'
            test = 'http://appt1456:8000/LATEST'
            dev = 'http://appd1454:8000/LATEST'

            # server aliases linked to URLs
            servers = {
                ('prod', 'production'): prod,
                ('test'): test,
                ('dev', 'development'): dev}

            for aliases in servers:
                if server in aliases:
                    self.url = servers[aliases]

        if self.url is None:
            raise ValueError("server '{}' not found in server aliases.".format(server))

    def set_lic_nbr(self, uri, lic_nbr, json_file=None, database='PhysicianSanctions'):
        # step 1, download current metadata file
        url = f'{self.url}/documents?uri={uri}&database={database}'

        # if json_file can be passed from a previous download, we don't need to re-download the file
        if json_file is None:
            # Download file
            response = self._connection.get(url=url,
                                            auth=self.auth)
            json_file = json.loads(response.content)

        # Fill in license number
        json_file['sanction']['physician']['license'] = lic_nbr

        # Upload edited file to update the document in MarkLogic
        response = self._connection.put(url,
                                        auth=self.auth,
                                        data=json.dumps(json_file))
        response.raise_for_status()
        return

    def set_me_nbr(self, uri, me_nbr, json_file=None, database='PhysicianSanctions'):
        url = f'{self.url}/documents?uri={uri}&database={database}'

        # if json_file can be passed from a previous download, we don't need to re-download the file
        if json_file is None:
            # Download file
            response = self._connection.get(url=url,
                                            auth=self.auth)
            json_file = json.loads(response.content)

        # Fill ME number
        json_file['sanction']['physician']['me'] = me_nbr
        json_file['app']['assignment']['me'] = me_nbr

        # Upload edited file to update the document in MarkLogic
        response = self._connection.put(url=url,
                                        auth=self.auth,
                                        data=json.dumps(json_file))
        response.raise_for_status()
