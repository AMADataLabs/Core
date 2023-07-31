""" Loader tasks for VeriCre profiles ETL. """
from   dataclasses import dataclass
import json
import logging
from   datalabs.parameter import add_schema
from   datalabs.task import Task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class VeriCreProfileSynchronizerParameters:
    host: str
    port: str
    execution_time: str = None


class VeriCreProfileSynchronizerTask(Task):
    PARAMETER_CLASS = VeriCreProfileSynchronizerParameters

    def run(self):
        ama_masterfile = json.loads(self._data[0].decode())

        payload = [{"entityId":x["entityId"]} for x in ama_masterfile]

        # TODO: call sync API endpoint

        return [json.dumps(payload).encode()]
