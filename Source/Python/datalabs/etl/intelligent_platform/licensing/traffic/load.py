""" Licensing traffic report loader task """
from   dataclasses import dataclass
from   datetime import datetime

from   datalabs.messaging.email_message import Attachment, send_email
from   datalabs.parameter import add_schema
from   datalabs.task import Task


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class TrafficReportSMTPLoaderParameters:
    to: str  # pylint: disable=invalid-name
    cc: str=None  # pylint: disable=invalid-name
    execution_time: str=None


class TrafficReportSMTPLoaderTask(Task):
    PARAMETER_CLASS = TrafficReportSMTPLoaderParameters

    def run(cls):
        date = str(datetime.now().date())  # 'YYYY-MM-DD'
        name = f'Intelligent_Platform_Traffic_Report_{date}.csv'
        report_csv_data = self._data[0]
        file = Attachment(name=name, data=report_csv_data)
        summary = '''Hello,
        This is an automated email from DataLabs.
        Attached is the latest Self-Service Licensing traffic data.
        '''

        send_email(
            to=self._parameters.to,
            cc=self._parameters.cc,
            subject=f'Self-Service Licensing Traffic Report - {date}',
            body=summary,
            attachments=[file],
            from_account='datalabs@ama-assn.org'
        )
