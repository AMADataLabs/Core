""" AMC Flagged Addresses Report loader task """
from dataclasses import dataclass
from datetime import datetime

# pylint: disable=import-error, invalid-name
from datalabs.etl.load import LoaderTask
from datalabs.messaging.email_message import Attachment, send_email
from datalabs.parameter import add_schema


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class AMCLoaderParameters:
    to: str or [str]
    cc: str or [str]
    body: str
    from_account: str
    data: [Attachment]


class AMCReportSMTPLoader(LoaderTask):
    PARAMETER_CLASS = AMCLoaderParameters

    def _load(self):
        date = str(datetime.now().date())  # 'YYYY-MM-DD'
        name = f'AMC_flagged_addresses_{date}.xlsx'
        file = Attachment(name=name, data=self._data[0])

        send_email(
            to=self._parameters.to,
            cc=self._parameters.cc,
            subject=f'AMC Sweep Results - {date}',
            body=self._parameters.body,
            attachments=[file],
            from_account=self._parameters.from_account

        )
