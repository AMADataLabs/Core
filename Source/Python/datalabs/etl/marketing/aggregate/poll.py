""" Release endpoint classes. """
from   dataclasses import dataclass
import io
import logging

from   datalabs.access.atdata import AtData
from   datalabs.etl.csv import CSVWriterMixin
from   datalabs.parameter import add_schema
from   datalabs.poll import ExternalConditionPollingTask
from   datalabs.task import Task

import pandas

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@add_schema
@dataclass
class AtDataStatusPollingTaskParameters:
    host: str
    account: str
    api_key: str


class AtDataStatusPollingTask(Task, ExternalConditionPollingTask, CSVWriterMixin):
    PARAMETER_CLASS = AtDataStatusPollingTaskParameters


    def __init__(self, parameters: AtDataStatusPollingTaskParameters, data: "list<bytes>"=None):
        super().__init__(parameters, data)
        self._request_id = ''
        self._file = None

    def run(self):
        inputs = self._parse_data(self._data[0])
        self._data = None

        self._request_id = inputs['request_id'].tolist()[0]

        output = self._create_request_id_dataframe()

        return [self._dataframe_to_csv(output)]

    @classmethod
    def _parse_data(cls, data):
        data = pandas.read_csv(
            io.BytesIO(data)
        )
        return data

    def _create_request_id_dataframe(self):
        flag = self._is_ready()

        return pandas.DataFrame(
                   data=dict(Request_id=self._request_id, Files=self._file, Flag=flag),
                   index=[0]
               )

    def _is_ready(self):
        ready = False

        atdata = AtData(self._parameters.host, self._parameters.account, self._parameters.api_key)

        status, self._file = atdata.get_validation_status(self._request_id)

        if status == "Returned":
            ready = True

        return ready
