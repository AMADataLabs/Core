""" AMC Flagged Addresses Report loader task """
from   dataclasses import dataclass
from   datetime import datetime
from   io import BytesIO
import pickle

# pylint: disable=import-error, invalid-name
from   datalabs.etl.load import LoaderTask
from   datalabs.messaging.email_message import Attachment, send_email
from   datalabs.parameter import add_schema


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class AMCReportSMTPLoaderParameters:
    to: str
    cc: str
    data: list

class AMCReportSMTPLoaderTask(LoaderTask):
    PARAMETER_CLASS = AMCReportSMTPLoaderParameters

    def _load(self):
        date = str(datetime.now().date())  # 'YYYY-MM-DD'
        name = f'AMC_flagged_addresses_{date}.xlsx'

        for data in self._parameters.data:
            report_data, summary = pickle.loads(data)
            file = Attachment(name=name, data=BytesIO(report_data))

            send_email(
                to=self._parameters.to,
                cc=self._parameters.cc,
                subject=f'AMC Sweep Results - {date}',
                body=summary,
                attachments=[file],
                from_account='datalabbs@ama-assn.org'
            )
