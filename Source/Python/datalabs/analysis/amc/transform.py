''' AMC Flagged Addresses Report generation task '''
from   dataclasses import dataclass

from   datalabs.analysis.amc.address import AddressReportParameters
from   datalabs.etl.transform import TransformerTask
from   datalabs.parameter import add_schema


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class FlaggedAddressReportParameters:
    to: str
    cc: str
    subject: str
    body: str
    from: str
    attachments: str
    data: object = None


class FlaggedAddressReportTask(TransformerTask):
    PARAMETER_CLASS = FlaggedAddressReportParameters

    def _transform(self):
        flagger = AMCAddressFlagger(this._parameters)

        # run() must return the report data as a list of byte strings
        return flagger.run()
