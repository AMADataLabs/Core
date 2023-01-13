""" AMC Flagged Addresses Report generation task """
from   dataclasses import dataclass
from   io import BytesIO
import logging
import pickle

import pandas

# pylint: disable=import-error, invalid-name
from   datalabs.analysis.amc.address import AMCAddressFlagger
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
class AMCAddressFlaggingTransformerTask(Task):
    PARAMETER_CLASS = AMCAddressFlaggingTransformerParameters

    def run(self):
        flagger = AMCAddressFlagger()

        data = [self._csv_to_dataframe(file) for file in self._data]

        results = [flagger.flag(file) for file in data]

        # returns list of bytes tuples, (xlsx_data, report_summary)
        LOGGER.debug('Returning %d results.', len(results))
        return [self._pickle(result) for result in results]

    @classmethod
    def _csv_to_dataframe(cls, file):
        return pandas.read_csv(BytesIO(file))

    @classmethod
    def _pickle(cls, result):
        return pickle.dumps(result)
