from dataclasses import dataclass
import os

from datalabs.parameter import add_schema
from datalabs.messaging.email_message import send_email
from datalabs.etl.load import LoaderTask


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class DBLReportEmailLoaderParameters:
    to: str
    cc: str = None


class DBLReportEmailLoaderTask(LoaderTask):
    PARAMETER_CLASS = DBLReportEmailLoaderParameters

    def _load(self):
        send_email(
            to=self._parameters.to,
            cc=self._parameters.cc,
            subject='Weekly DBL Report',
            body='Attached is the auto-generated DBL report file.',
            from_account='DataLabs@ama-assn.org',
            attachments=self._data
        )
