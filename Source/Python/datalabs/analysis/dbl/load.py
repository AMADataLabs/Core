import os

from datalabs.messaging.email_message import send_email
from datalabs.etl.load import LoaderTask
from datalabs.etl.fs.load import LocalUnicodeTextFileLoaderTask


class DBLReportEmailLoaderTask(LoaderTask):
    def __init__(self, parameters):
        super().__init__(parameters)

    def _load(self):
        send_email(
            to=self._parameters['to'],
            cc=self._parameters['cc'],
            subject=self._parameters['subject'],
            body=self._parameters['body'],
            from_account=self._parameters['from_account'],
            attachments=self._parameters['data']
        )
