""" Developer emails report loader task """
from   dataclasses import dataclass
from   datetime import datetime

from   datalabs.messaging.email_message import Attachment, send_email
from   datalabs.parameter import add_schema
from   datalabs.task import Task


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class EmailReportSMTPLoaderParameters:
    to: str  # pylint: disable=invalid-name
    cc: str = None  # pylint: disable=invalid-name
    execution_time: str = None


class EmailReportSMTPLoaderTask(Task):
    PARAMETER_CLASS = EmailReportSMTPLoaderParameters

    def run(self):
        date = str(datetime.now().date())  # 'YYYY-MM-DD'
        name = f'developer_emails_{date}.csv'
        report_csv_data = self._data[0]
        file = Attachment(name=name, data=report_csv_data)
        summary = '''
Hi,

This is an automated email from DataLabs.

Attached are the latest CPT Developer Program user emails.
'''

        send_email(
            to=self._parameters.to,
            cc=self._parameters.cc,
            subject=f'CPT Developer Program User Emails - {date}',
            body=summary,
            attachments=[file],
            from_account='datalabs@ama-assn.org'
        )

