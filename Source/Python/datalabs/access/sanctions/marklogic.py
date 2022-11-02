""" MarkLogic connection operations """
# pylint: disable=import-error
from   dataclasses import dataclass
import json
import os

from datalabs.access import marklogic as ml
from   datalabs.parameter import add_schema


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class MarkLogicParameters:
    host: str
    username: str
    password: str
    protocol: str="http"
    port: str="8000"
    version: str="LATEST"


class MarkLogic(ml.MarkLogic):
    def set_license_number(self, uri, license_number, json_file=None, database='PhysicianSanctions'):
        if json_file is None:
            json_file = self.get_file(uri=uri, database=database)

        # Fill license number
        json_file['sanction']['physician']['license'] = license_number

        self._set_file(uri=uri, data=json.dumps(json_file))

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
