""" Cerner report SMTP loader task """
from   dataclasses import dataclass
from   datetime import datetime

from   datalabs.etl.load import FileLoaderTask
from   datalabs.messaging.email_message import create_message, Attachment
from   datalabs.parameter import add_schema
from   datalabs.task import Task


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class SMTPFileLoaderParameters(FileLoaderTask):
    to_addresses: str  # pylint: disable=invalid-name
    subject: str
    message: str
    files: str
    cc_addresses: str = None  # pylint: disable=invalid-name
    execution_time: str = None


class SMTPLoaderTask(Task):
    PARAMETER_CLASS = SMTPLoaderParameters
    SMTP_SERVER = "amamx.ama-assn.org"
    FROM_ADDRESS = "datalabs@ama-assn.org"

    def _get_client(self):
        return smtplib.SMTP(self.SMTP_SERVER)

    def _get_files(self):
        return [file.strip() for file in self._parameters.files.split(',')]

    def _load_files(self, data, files):
        attachements = super()._load_files(data, files)

        message = create_message(
            self._parameters.to_addresses,
            self._parameters.cc_addresses,
            self._parameters.subject,
            self._parameters.message,
            attachements,
            self.FROM_ADDRESS,
            None
        )

        self._client.send_message(message)

    def _load_file(self, data, file):
        return Attachment(name=file, data=data)
