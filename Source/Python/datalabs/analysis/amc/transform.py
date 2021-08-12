""" AMC Flagged Addresses Report generation task """
from   dataclasses import dataclass
from   io import BytesIO
import pickle

import pandas

# pylint: disable=import-error, invalid-name
from datalabs.analysis.amc.address import AMCAddressFlagger
from datalabs.etl.transform import TransformerTask
from datalabs.parameter import add_schema


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class AMCAddressFlaggingTransformerParameters:
    data: list


# pylint: disable=no-self-use
class AMCAddressFlaggingTransformerTask(TransformerTask):
    PARAMETER_CLASS = AMCAddressFlaggingTransformerParameters

    def _transform(self):
        flagger = AMCAddressFlagger()

        data = [self._csv_to_dataframe(file) for file in self._parameters.data]

        results = [flagger.flag(file) for file in data]

        # returns list of bytes tuples, (xlsx_data, report_summary)
        return [self._pickle(result) for result in results]

    @classmethod
    def _csv_to_dataframe(cls, file):
        return pandas.read_csv(BytesIO(file))

    @classmethod
    def _pickle(cls, result):
        return pickle.dumps(result)
