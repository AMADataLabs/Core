""" Release endpoint classes. """
from   dataclasses import dataclass
import logging

from   datalabs.access.atdata import AtData
from   datalabs.parameter import add_schema
from   datalabs.poll import ExternalConditionPollingTask


logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@add_schema
@dataclass
class AtDataStatusPollingTaskParameters:
    host: str
    account: str
    api_key: str

class AtDataStatusPollingTask(ExternalConditionPollingTask):
    PARAMETER_CLASS = AtDataStatusPollingTaskParameters

    def _is_ready(self, request_parameters):
        ready = False
        atdata = AtData(self._parameters.host, self._parameters.account, self._parameters.api_key)

        status, request_parameters["results_filename"] = atdata.get_validation_status(request_parameters["request_id"])
        results_parameters = [request_parameters["request_id"], request_parameters["results_filename"]]

        if status == "Returned":
            ready = True

        return (ready, results_parameters)
