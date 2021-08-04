""" AMC Flagged Addresses Report generation task """

# pylint: disable=import-error, invalid-name
from datalabs.analysis.amc.address import AMCAddressFlagger
from datalabs.etl.transform import TransformerTask


# pylint: disable=no-self-use
class AMCAddressFlaggingTransformerTask(TransformerTask):
    def _transform(self):
        flagger = AMCAddressFlagger()

        return [flagger.flag(file) for file in self._data] # returns list of Bytes-like, [xlsx_data, report_summary]
