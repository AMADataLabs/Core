""" AMC Flagged Addresses Report generation task """
from dataclasses import dataclass

# pylint: disable=import-error, invalid-name
from datalabs.analysis.amc.address import AMCAddressFlagger
from datalabs.etl.transform import TransformerTask
from datalabs.parameter import add_schema


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class FlaggedAddressReportParameters:
    to: str
    cc: str
    subject: str
    body: str
    from_account: str
    attachments: str
    data: object = None


# pylint: disable=no-self-use
class FlaggedAddressReportTask(TransformerTask):
    # PARAMETER_CLASS = FlaggedAddressReportParameters  # these parameters are required for loader, not transformer

    def _transform(self):
        flagger = AMCAddressFlagger()

        # run() must return the report data as a list of byte strings
        return flagger.run()
