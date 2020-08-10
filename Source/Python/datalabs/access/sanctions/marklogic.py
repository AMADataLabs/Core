import json
import os
from requests.auth import HTTPDigestAuth
from datalabs.access import marklogic as ml


class MarkLogic(ml.MarkLogic):
    def __init__(self, key=None, host=None):
        if key:
            host = os.environ[f'MARKLOGIC_HOST_{key.upper()}']
        if host is None:
            raise ValueError(f"Host '{host}' not found in server aliases.")
        self.url = f'http://{host}:8000/LATEST'
        super().__init__()
        self.auth = HTTPDigestAuth(self._credentials.username, self._credentials.password)

    def set_license_number(self, uri, license_number, json_file=None, database='PhysicianSanctions'):
        if json_file is None:
            json_file = self.get_file(uri=uri, database=database)

        # Fill license number
        json_file['sanction']['physician']['license'] = license_number

        self._set_file(uri=uri, data=json.dumps(json_file))
        return

    def set_me_number(self, uri, me_nbr, json_file=None, database='PhysicianSanctions'):
        if json_file is None:
            json_file = self.get_file(uri=uri, database=database)

        # Fill ME number
        json_file['sanction']['physician']['me'] = me_nbr
        json_file['app']['assignment']['me'] = me_nbr

        self._set_file(uri=uri, data=json.dumps(json_file))

    def _set_file(self, uri, data, database='PhysicianSanctions'):
        url = f'{self.url}/documents?uri={uri}&database={database}'
        response = self._connection.put(url=url, auth=self.auth, data=data)
        response.raise_for_status()
