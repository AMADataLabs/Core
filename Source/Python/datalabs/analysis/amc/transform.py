""" AMC Flagged Addresses Report generation task """

# pylint: disable=import-error, invalid-name
from datalabs.analysis.amc.address import AMCAddressFlagger
from datalabs.etl.transform import TransformerTask


# pylint: disable=no-self-use
class FlaggedAddressReportTask(TransformerTask):
    # PARAMETER_CLASS = FlaggedAddressReportParameters  # these parameters are required for loader, not transformer

    def _transform(self):
        flagger = AMCAddressFlagger()  # returns Bytes-like, [xlsx_data, report_summary]

        # run() must return the report data as a list of byte strings
        return flagger.run()
