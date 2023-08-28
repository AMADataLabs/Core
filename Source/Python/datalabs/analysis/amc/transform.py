""" AMC Flagged Addresses Report generation task """
from   dataclasses import dataclass
import logging
import pickle

# pylint: disable=import-error, invalid-name
from   datalabs.analysis.amc.address import AMCAddressFlagger
from   datalabs.etl.csv import CSVReaderMixin
from   datalabs.parameter import add_schema
from   datalabs.task import Task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class AMCAddressFlaggingTransformerParameters:
    execution_time: str = None


# pylint: disable=no-self-use
class AMCAddressFlaggingTransformerTask(CSVReaderMixin, Task):
    PARAMETER_CLASS = AMCAddressFlaggingTransformerParameters

    def run(self):
        flagger = AMCAddressFlagger()

        data = self._csv_to_dataframe(self._data[0])

        deduped_data = self._dedupe(data)

        results = flagger.flag(deduped_data)  # list of bytes tuples, (xlsx_data, report_summary)

        return [self._pickle(results)]

    @classmethod
    def _dedupe(cls, data):
        return data[data.name_type == "LN"].drop(columns="name_type")

    @classmethod
    def _pickle(cls, result):
        return pickle.dumps(result)
