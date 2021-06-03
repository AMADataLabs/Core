from dataclasses import dataclass
import os

from datalabs.parameter import add_schema
from datalabs.messaging.email_message import send_email
from datalabs.etl.load import LoaderTask
from datalabs.etl.fs.load import LocalUnicodeTextFileLoaderTask  # tbd


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class DBLReportEmailLoaderParameters:
    to: str
    cc: str
    subject: str
    body: str
    from_account: str


class DBLReportEmailLoaderTask(LoaderTask):
    PARAMETER_CLASS = DBLReportEmailLoaderParameters

    def _load(self):
        send_email(
            to=self._parameters.to,
            cc=self._parameters.cc,
            subject=self._parameters.subject,
            body=self._parameters.body,
            from_account=self._parameters.from_account,
            attachments=self._parameters['data']
        )
