""" Cerner report SMTP loader task """
from   dataclasses import dataclass
from   datetime import datetime

import smtplib

from   datalabs.etl.load import FileLoaderTask
from   datalabs.messaging.email_message import create_message, Attachment
from   datalabs.parameter import add_schema


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class SMTPFileLoaderParameters:
    to_addresses: str  # pylint: disable=invalid-name
    subject: str
    message: str
    files: str
    cc_addresses: str = None  # pylint: disable=invalid-name
    execution_time: str = None


class SMTPFileLoaderTask(FileLoaderTask):
    PARAMETER_CLASS = SMTPFileLoaderParameters
    SMTP_SERVER = "amamx.ama-assn.org"
    FROM_ADDRESS = "datalabs@ama-assn.org"

    def _get_client(self):
        return smtplib.SMTP(self.SMTP_SERVER)

    def _get_files(self):
        return [file.strip() for file in self._parameters.files.split(',')]

    def _load_file(self, data, file):
        pass

    def _load_files(self, data, files):
        attachments = [Attachment(name=file, data=data) for file, data in zip(files, data)]

        message = create_message(
            self._parameters.to_addresses,
            datetime.strftime(self.execution_time, self._parameters.subject),
            cc=self._parameters.cc_addresses,
            body=self._parameters.message,
            attachments=attachments,
            from_account=self.FROM_ADDRESS,
            html_content=None
        )

        self._client.send_message(message)
