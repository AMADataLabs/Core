from dataclasses import dataclass
from datetime import datetime

from datalabs.etl.load import LoaderTask
from datalabs.messaging.email_message import send_email, Attachment
from datalabs.parameter import add_schema


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class DBLReportEmailLoaderParameters:
    to: str or [str]
    cc: str or [str] = ''
    data: object = None


class DBLReportEmailLoaderTask(LoaderTask):
    PARAMETER_CLASS = DBLReportEmailLoaderParameters

    def _load(self):
        today = str(datetime.now().date())
        subject = f'Weekly DBL Report - {today}'
        attachment = Attachment(subject + '.xlsx', data=self._parameters.data[0])
        send_email(
            to=self._parameters.to,
            cc=self._parameters.cc,
            subject=subject,
            body='',
            from_account='datalabs@ama-assn.org',
            attachments=[attachment]
        )
