""" AMC Flagged Addresses Report generation task """

# pylint: disable=import-error, invalid-name
from datalabs.analysis.amc.address import AMCAddressFlagger
from datalabs.etl.transform import TransformerTask


# pylint: disable=no-self-use
class AMCAddressFlaggingTransformer(TransformerTask):
    def _transform(self):
        flagger = AMCAddressFlagger(self._data)  # returns list of Bytes-like, [xlsx_data, report_summary]

        return flagger.run()
