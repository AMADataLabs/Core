""" Email Report loader task """
from   dataclasses import dataclass
from   datetime import datetime
import pickle
# pylint: disable=import-error, invalid-name
from   datalabs.etl.load import LoaderTask
from   datalabs.messaging.email_message import Attachment, send_email
from   datalabs.parameter import add_schema


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class EmailReportSMTPLoaderParameters:
    to: str
    data: list
    cc: str = None
    execution_time: str = None

class EmailReportSMTPLoaderTask(LoaderTask):
    PARAMETER_CLASS = EmailReportSMTPLoaderParameters

    def _load(self):
        date = str(datetime.now().date())  # 'YYYY-MM-DD'
        name = f'Developer_emails_{date}.csv'

        for data in self._parameters.data:
            report_csv_data = pickle.loads(data[0])
            file = Attachment(name=name, data=report_csv_data)
            summary = f'''Hi,This is an automated email from DataLabs. Please find all new content in attachments.'''
            send_email(
                to=self._parameters.to,
                cc=self._parameters.cc,
                subject=f'CPT Developer Program User Emails - {date}',
                body=summary,
                attachments=[file],
                from_account='datalabs@ama-assn.org'
            )
