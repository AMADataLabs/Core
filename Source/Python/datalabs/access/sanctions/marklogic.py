import json
import os
from requests.auth import HTTPDigestAuth
from datalabs.access import marklogic as ml


class MarkLogic(ml.MarkLogic):
    def __init__(self, key=None, host=None):
        if host is None:
            host = os.environ[f'DATABASE_{self._key.upper()}_HOST']

        self.url = f'http://{host}:8000/LATEST'
        super().__init__(credentials=None, key=key)
        self.auth = HTTPDigestAuth(self._credentials.username, self._credentials.password)

    def set_license_number(self, uri, license_number, json_file=None, database='PhysicianSanctions'):
        if json_file is None:
            json_file = self.get_file(uri=uri, database=database)

        # Fill license number
        json_file['sanction']['physician']['license'] = license_number

        self._set_file(uri=uri, data=json.dumps(json_file))
        return

    def set_me_number(self, uri, me_number, json_file=None, database='PhysicianSanctions'):
        if json_file is None:
            json_file = self.get_file(uri=uri, database=database)

        # Fill ME number
        json_file['sanction']['physician']['me'] = me_number
        json_file['app']['assignment']['me'] = me_number

        self._set_file(uri=uri, data=json.dumps(json_file))

    def _set_file(self, uri, data, database='PhysicianSanctions'):
        url = f'{self.url}/documents?uri={uri}&database={database}'
        response = self._connection.put(url=url, auth=self.auth, data=data)
        response.raise_for_status()
