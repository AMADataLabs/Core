""" Loader tasks for VeriCre profiles ETL. """
from   dataclasses import dataclass
import json
import logging
import requests

from   datalabs.parameter import add_schema
from   datalabs.task import Task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


@add_schema
@dataclass
# pylint: disable=too-many-instance-attribucleartes
class VeriCreProfileSynchronizerParameters:
    host: str
    port: str = None
    execution_time: str = None


class VeriCreProfileSynchronizerTask(Task):
    PARAMETER_CLASS = VeriCreProfileSynchronizerParameters

    def run(self):
        for item in self._data:
            ama_masterfile = json.loads(item.decode())
            payload = [{"entityId":x["entityId"]} for x in ama_masterfile]
            self._make_request(payload)

    def _make_request(self, payload):
        port = ''
        if self._parameters.port:
            port = ":" + self._parameters.port

        url = f'https://{self._parameters.host}{port}/users/physicians/onETLSync'
        headers = {'Content-Type': 'application/json'}

        try:
            requests.post(
                url, data=json.dumps(payload), headers=headers, verify=False
            )
        except requests.exceptions.RequestException as request_exception:
            print("Error making the API call:", request_exception)
