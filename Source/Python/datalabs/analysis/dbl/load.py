""" DBL report email loader task class """

from dataclasses import dataclass
from datetime import datetime

# pylint: disable=import-error
from datalabs.etl.load import LoaderTask
from datalabs.messaging.email_message import send_email, Attachment
from datalabs.parameter import add_schema


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes, invalid-name
class DBLReportEmailLoaderParameters:
    to: str
    cc: str
    data: list
    execution_time: str = None


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
            body='Attached is the auto-generated DBL report file.',
            from_account='datalabs@ama-assn.org',
            attachments=[attachment]
        )
