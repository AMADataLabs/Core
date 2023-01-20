""" AMC Flagged Addresses Report loader task """
from   dataclasses import dataclass
from   datetime import datetime
import pickle

from   datalabs.messaging.email_message import Attachment, send_email
from   datalabs.parameter import add_schema
from   datalabs.task import Task


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class AMCReportSMTPLoaderParameters:
    to: str  # pylint: disable=invalid-name
    cc: str = None  # pylint: disable=invalid-name
    execution_time: str = None

class AMCReportSMTPLoaderTask(Task):
    PARAMETER_CLASS = AMCReportSMTPLoaderParameters

    def run(self):
        date = str(datetime.now().date())  # 'YYYY-MM-DD'
        name = f'AMC_flagged_addresses_{date}.xlsx'

        for data in self._data:
            report_data, summary = pickle.loads(data)
            file = Attachment(name=name, data=report_data)

            send_email(
                to=self._parameters.to,
                cc=self._parameters.cc,
                subject=f'AMC Sweep Results - {date}',
                body=summary,
                attachments=[file],
                from_account='datalabs@ama-assn.org'
            )
